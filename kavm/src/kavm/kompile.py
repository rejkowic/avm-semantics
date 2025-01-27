import logging
import subprocess
from pathlib import Path
from subprocess import CalledProcessError, CompletedProcess
from typing import Final, List, Optional

from kavm.kavm import KAVM

_LOGGER: Final = logging.getLogger(__name__)
_LOG_FORMAT: Final = '%(levelname)s %(asctime)s %(name)s - %(message)s'


def kompile(
    definition_dir: Path,
    main_file: Path,
    includes: Optional[List[Path]] = None,
    main_module_name: Optional[str] = None,
    syntax_module_name: Optional[str] = None,
    backend: Optional[str] = 'llvm',
    md_selector: Optional[str] = None,
    verbose: bool = True,
    hook_namespaces: Optional[List[str]] = None,
    hook_cpp_files: Optional[List[Path]] = None,
    hook_clang_flags: Optional[List[str]] = None,
    coverage: bool = False,
    gen_bison_parser: bool = False,
    emit_json: bool = True,
) -> KAVM:
    if backend == 'llvm':
        generate_interpreter(
            definition_dir,
            main_file,
            includes,
            main_module_name,
            syntax_module_name,
            md_selector,
            hook_namespaces,
            hook_cpp_files,
            hook_clang_flags,
            coverage=coverage,
            gen_bison_parser=gen_bison_parser,
        )
    elif backend == 'haskell':
        kompile_haskell(
            definition_dir=definition_dir,
            main_file=main_file,
            includes=includes,
            main_module_name=main_module_name,
            syntax_module_name=syntax_module_name,
            md_selector=md_selector,
            hook_namespaces=hook_namespaces,
            backend=backend,
            verbose=verbose,
            emit_json=emit_json,
        )
    return KAVM(definition_dir)


def kompile_haskell(
    definition_dir: Path,
    main_file: Path,
    includes: Optional[List[Path]] = None,
    main_module_name: Optional[str] = None,
    syntax_module_name: Optional[str] = None,
    md_selector: Optional[str] = None,
    hook_namespaces: Optional[List[str]] = None,
    backend: Optional[str] = 'llvm',
    verbose: bool = True,
    emit_json: bool = True,
) -> CompletedProcess:
    command = [
        'kompile',
        '--output-definition',
        str(definition_dir),
        str(main_file),
    ]

    command += ['--verbose'] if verbose else []
    command += ['--emit-json'] if emit_json else []
    command += ['--backend', backend] if backend else []
    command += ['--main-module', main_module_name] if main_module_name else []
    command += ['--syntax-module', syntax_module_name] if syntax_module_name else []
    command += ['--md-selector', md_selector] if md_selector else []
    command += ['--hook-namespaces', ' '.join(hook_namespaces)] if hook_namespaces else []
    command += ['--concrete-rules', ','.join(KAVM.concrete_rules())]
    command += [str(arg) for include in includes for arg in ['-I', include]] if includes else []

    _LOGGER.info(' '.join(command))

    return subprocess.run(command, check=True, text=True)


def generate_interpreter(
    definition_dir: Path,
    main_file: Path,
    includes: Optional[List[Path]] = None,
    main_module_name: Optional[str] = None,
    syntax_module_name: Optional[str] = None,
    md_selector: Optional[str] = None,
    hook_namespaces: Optional[List[str]] = None,
    hook_cpp_files: Optional[List[Path]] = None,
    hook_clang_flags: Optional[List[str]] = None,
    coverage: bool = False,
    gen_bison_parser: bool = False,
) -> None:
    '''Kompile KAVM to produce an LLVM-based interpreter'''

    interpreter_object_file = definition_dir / 'partial.o'
    interpreter_executable_file = definition_dir / 'interpreter'

    def _kompile_partial() -> None:
        command = [
            'kompile',
            '--output-definition',
            str(definition_dir),
            str(main_file),
        ]

        command += ['--verbose']
        command += ['--emit-json']
        command += ['--gen-glr-bison-parser'] if gen_bison_parser else []
        command += ['--main-module', main_module_name] if main_module_name else []
        command += ['--syntax-module', syntax_module_name] if syntax_module_name else []
        command += [str(arg) for include in includes for arg in ['-I', include]] if includes else []
        command += ['--md-selector', md_selector] if md_selector else []
        command += ['--hook-namespaces', ' '.join(hook_namespaces)] if hook_namespaces else []
        command += ['-ccopt', '-c', '-ccopt', '-o', '-ccopt', str(interpreter_object_file)]
        command += ['--coverage'] if coverage else []
        try:
            subprocess.run(command, check=True, text=True)
        except CalledProcessError:
            print(' '.join(map(str, command)))
            raise

    def _llvm_kompile(
        interpreter_object_file: Path,
        interpreter_executable_file: Path,
        hook_cpp_files: Optional[List[Path]] = None,
        hook_clang_flags: Optional[List[str]] = None,
    ) -> None:
        command = ['llvm-kompile', str(interpreter_object_file), 'main', '--']

        command += [str(path) for path in hook_cpp_files] if hook_cpp_files else []
        command += ['-o', str(interpreter_executable_file)]
        command += [flag.strip() for flag in hook_clang_flags] if hook_clang_flags else []

        try:
            print(' '.join(map(str, command)))
            subprocess.run(command, check=True, text=True)
        except CalledProcessError:
            print(' '.join(map(str, command)))
            raise

    _kompile_partial()
    _llvm_kompile(
        interpreter_object_file=interpreter_object_file.resolve(),
        interpreter_executable_file=interpreter_executable_file.resolve(),
        hook_cpp_files=hook_cpp_files,
        # includes=includes,
        hook_clang_flags=hook_clang_flags,
    )
