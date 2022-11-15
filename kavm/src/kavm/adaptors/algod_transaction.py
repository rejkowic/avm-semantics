from base64 import b64decode, b64encode
from typing import Any, Dict, List, Optional, OrderedDict, cast

from algosdk.constants import APPCALL_TXN, ASSETTRANSFER_TXN, PAYMENT_TXN
from algosdk.encoding import encode_address
from algosdk.future.transaction import (
    ApplicationCallTxn,
    AssetTransferTxn,
    OnComplete,
    PaymentTxn,
    StateSchema,
    SuggestedParams,
    Transaction,
)
from pyk.kast import KApply, KInner, KSort, KToken, Subst
from pyk.kastManip import free_vars, split_config_from

from kavm.pyk_utils import maybe_tvalue, tvalue, tvalue_list


class KAVMApplyData:
    '''
    KAVM encoding of transaction apply data: effects of an approved transaction

    See avm-semantics/lib/include/kframework/avm/txn.md for the K configuration
    '''

    def __init__(
        self,
        tx_scratch: Optional[Dict[int, Any]] = None,
        inner_txns: Optional[List[int]] = None,
        tx_config_asset: int = 0,
        tx_application_id: int = 0,
        log_size: int = 0,
        log_data: Optional[List[Any]] = None,
    ):
        self._tx_scratch: Dict[int, Any] = tx_scratch if tx_scratch else {}
        self._inner_txns: List[int] = inner_txns if inner_txns else []
        self._tx_config_asset = tx_config_asset
        self._tx_application_id = tx_application_id
        self._log_size = log_size
        self._log_data: List[Any] = log_data if log_data else []

    @staticmethod
    def from_k_cell(kast_term: KInner) -> 'KAVMApplyData':
        """
        Construct an instance of KAVMApplyData from a K <applyData> cell

        Raise ValueError if the term is marformed
        """
        (_, subst) = split_config_from(kast_term)
        return KAVMApplyData(
            tx_scratch={},  # tx_scratch=subst['TXSCRATCH_CELL'],
            inner_txns=[],  # inner_txns=subst['INNERTXNS_CELL'],
            tx_config_asset=int(cast(KToken, subst['TXCONFIGASSET_CELL']).token),
            tx_application_id=int(cast(KToken, subst['TXAPPLICATIONID_CELL']).token),
            log_size=int(cast(KToken, subst['LOGSIZE_CELL']).token),
            log_data=[],  # log_data=subst['LOGDATA_CELL'],
        )


class KAVMTransaction(Transaction):
    """
    Convenience class represenring an Algorandtransaction in KAVM
    """

    _apply_data = KAVMApplyData()

    def pending_transaction_responce(self) -> Dict[str, Any]:
        """A dictionary representing PendingTransactionResponse for this tranasction"""
        return {
            "asset-index": self._apply_data._tx_config_asset if self._apply_data else 0,
            "application-index": self._apply_data._tx_application_id if self._apply_data else 0,
            "close-rewards": 0,
            "closing-amount": 0,
            "asset-closing-amount": 0,
            "confirmed-round": 1,
            "receiver-rewards": 0,
            "sender-rewards": 0,
            "local-state-delta": None,
            "global-state-delta": None,
            "logs": self._apply_data._log_data if self._apply_data else None,
            "inner-txns": self._apply_data._inner_txns if self._apply_data else None,
            "txn": None,
        }

    @staticmethod
    def sanitize_byte_fields(txn_dict: OrderedDict[str, Any]) -> OrderedDict[str, Any]:
        """Convert bytes fields of Transaction into base64-encoded strigns"""
        for k, v in txn_dict.items():
            if type(v) is bytes:
                if k in ['snd', 'rcv', 'close']:
                    txn_dict[k] = encode_address(v)
                else:
                    txn_dict[k] = b64encode(v).decode('utf8')
        return txn_dict

    @staticmethod
    def from_k_cell(kast_term: KInner) -> 'KAVMTransaction':
        """
        Covert a Kast term to one of the subclasses of the algosdk.Transaction

        Raise ValueError if the transaction is marformed
        """
        (_, tx_cell_subst) = split_config_from(kast_term)

        sp = SuggestedParams(
            int(cast(KToken, tx_cell_subst['FEE_CELL']).token),
            int(cast(KToken, tx_cell_subst['FIRSTVALID_CELL']).token),
            int(cast(KToken, tx_cell_subst['LASTVALID_CELL']).token),
            cast(KToken, tx_cell_subst['GENESISHASH_CELL']).token,
            flat_fee=True,
        )

        tx_type = cast(KToken, tx_cell_subst['TXTYPE_CELL']).token.strip('"')
        result = None
        if tx_type == PAYMENT_TXN:
            result = PaymentTxn(
                sender=cast(KToken, tx_cell_subst['SENDER_CELL']).token.strip('"'),
                sp=sp,
                receiver=cast(KToken, tx_cell_subst['RECEIVER_CELL']).token.strip('"'),
                amt=int(cast(KToken, tx_cell_subst['AMOUNT_CELL']).token),
            )
        elif tx_type == ASSETTRANSFER_TXN:
            result = AssetTransferTxn(
                sender=cast(KToken, tx_cell_subst['SENDER_CELL']).token.strip('"'),
                sp=sp,
                receiver=cast(KToken, tx_cell_subst['ASSETRECEIVER_CELL']).token.strip('"'),
                amt=int(cast(KToken, tx_cell_subst['ASSETAMOUNT_CELL']).token.strip('"')),
                index=int(cast(KToken, tx_cell_subst['XFERASSET_CELL']).token.strip('"')),
            )
        elif tx_type == APPCALL_TXN:
            result = ApplicationCallTxn(
                sender=cast(KToken, tx_cell_subst['SENDER_CELL']).token.strip('"'),
                sp=sp,
                index=int(cast(KToken, tx_cell_subst['APPLICATIONID_CELL']).token.strip('"')),
                on_complete=OnComplete(int(cast(KToken, tx_cell_subst['ONCOMPLETION_CELL']).token.strip('"'))),
                local_schema=StateSchema(
                    int(cast(KToken, tx_cell_subst['LOCALNUI_CELL']).token.strip('"')),
                    int(cast(KToken, tx_cell_subst['LOCALNBS_CELL']).token.strip('"')),
                ),
                global_schema=StateSchema(
                    int(cast(KToken, tx_cell_subst['GLOBALNUI_CELL']).token.strip('"')),
                    int(cast(KToken, tx_cell_subst['GLOBALNBS_CELL']).token.strip('"')),
                ),
                approval_program=b64decode(
                    cast(KToken, tx_cell_subst['APPROVALPROGRAM_CELL']).token.strip('"')
                    if hasattr(tx_cell_subst['APPROVALPROGRAM_CELL'], 'token')
                    else ''
                ),
                clear_program=b64decode(
                    cast(KToken, tx_cell_subst['CLEARSTATEPROGRAM_CELL']).token.strip('"')
                    if hasattr(tx_cell_subst['CLEARSTATEPROGRAM_CELL'], 'token')
                    else ''
                ),
                # TODO: handle array fields
                app_args=None,
                accounts=None,
                foreign_apps=None,
                foreign_assets=None,
                extra_pages=0,
            )
            # apply_data = KAVMApplyData(
            #     tx_config_asset=int(cast(KToken, tx_cell_subst['TXCONFIGASSET_CELL']).token.strip('"')),
            #     tx_application_id=int(cast(KToken, tx_cell_subst['TXAPPLICATIONID_CELL']).token.strip('"')),
            # )
        else:
            raise ValueError(f'Cannot instantiate a Transaction of an unexpected type {tx_type}')
        return result


def txn_type_to_type_enum(txn_type: str) -> int:
    if txn_type == 'unknown':
        return 0
    elif txn_type == 'pay':
        return 1
    elif txn_type == 'keyreg':
        return 2
    elif txn_type == 'acfg':
        return 3
    elif txn_type == 'axfer':
        return 4
    elif txn_type == 'afrz':
        return 5
    elif txn_type == 'appl':
        return 6
    else:
        raise ValueError(f'unknown transaction type {txn_type}')


def transaction_k_term(kavm: Any, txn: Transaction, txid: str) -> KInner:
    """Convert a Transaction objet to a K cell"""
    empty_transaction_cell = kavm.definition.empty_config(KSort('TransactionCell'))

    header_subst = Subst(
        {
            'FEE_CELL': maybe_tvalue(txn.fee),
            'FIRSTVALID_CELL': maybe_tvalue(txn.first_valid_round),
            'LASTVALID_CELL': maybe_tvalue(txn.last_valid_round),
            'GENESISHASH_CELL': maybe_tvalue(txn.genesis_hash),
            'GENESISID_CELL': maybe_tvalue(txn.genesis_id),
            'SENDER_CELL': KToken(txn.sender.strip("'"), KSort('TAddressLiteral')),
            'TXTYPE_CELL': maybe_tvalue(txn.type),
            'TYPEENUM_CELL': maybe_tvalue(txn_type_to_type_enum(txn.type)),
            'GROUPIDX_CELL': maybe_tvalue(txn.group),
            'GROUPID_CELL': KToken('"0"', KSort('String')),
            'LEASE_CELL': maybe_tvalue(txn.lease),
            'NOTE_CELL': maybe_tvalue(txn.note),
            'REKEYTO_CELL': maybe_tvalue(txn.rekey_to),
            'TXCONFIGASSET_CELL': tvalue(0),
            'TXAPPLICATIONID_CELL': tvalue(0),
            'INNERTXNS_CELL': KApply('.List'),
            'LOGSIZE_CELL': tvalue(0),
            'LOGDATA_CELL': tvalue_list([]),
            'RESUME_CELL': KToken('false', KSort('Bool')),
            'TXSCRATCH_CELL': KApply('.Map'),
        }
    )
    type_specific_subst = None
    if txn.type == PAYMENT_TXN:
        txn = cast(PaymentTxn, txn)
        type_specific_subst = Subst(
            {
                'RECEIVER_CELL': KToken(txn.receiver.strip("'"), KSort('TAddressLiteral')),
                'AMOUNT_CELL': maybe_tvalue(txn.amt),
                'CLOSEREMAINDERTO_CELL': maybe_tvalue(txn.close_remainder_to),
            }
        )
    if txn.type == ASSETTRANSFER_TXN:
        raise NotImplementedError()
    if txn.type == APPCALL_TXN:
        txn = cast(ApplicationCallTxn, txn)
        type_specific_subst = Subst(
            {
                'APPLICATIONID_CELL': maybe_tvalue(txn.index),
                'ONCOMPLETION_CELL': maybe_tvalue(int(txn.on_complete))
                if txn.on_complete is not None
                else maybe_tvalue(0),
                'ACCOUNTS_CELL': tvalue_list(txn.accounts) if txn.accounts is not None else tvalue_list([]),
                'APPROVALPROGRAM_CELL': maybe_tvalue(txn.approval_program),
                'APPROVALPROGRAMSRC_CELL': maybe_tvalue(txn.approval_program)
                if txn.approval_program
                else kavm.parse_teal('int 1'),
                'CLEARSTATEPROGRAM_CELL': maybe_tvalue(txn.clear_program),
                'CLEARSTATEPROGRAMSRC_CELL': maybe_tvalue(txn.clear_program)
                if txn.clear_program
                else kavm.parse_teal('int 1'),
                'APPLICATIONARGS_CELL': tvalue_list(txn.app_args if txn.app_args else []),
                'FOREIGNAPPS_CELL': tvalue_list(txn.foreign_apps if txn.foreign_apps else []),
                'FOREIGNASSETS_CELL': tvalue_list(txn.foreign_assets)
                if txn.foreign_assets is not None
                else tvalue_list([]),
                'GLOBALNUI_CELL': maybe_tvalue(txn.global_schema.num_uints)
                if txn.global_schema is not None
                else maybe_tvalue(0),
                'GLOBALNBS_CELL': maybe_tvalue(txn.global_schema.num_byte_slices)
                if txn.global_schema is not None
                else maybe_tvalue(0),
                'LOCALNUI_CELL': maybe_tvalue(txn.local_schema.num_uints)
                if txn.local_schema is not None
                else maybe_tvalue(0),
                'LOCALNBS_CELL': maybe_tvalue(txn.local_schema.num_byte_slices)
                if txn.local_schema is not None
                else maybe_tvalue(0),
                'EXTRAPROGRAMPAGES_CELL': maybe_tvalue(txn.extra_pages)
                if txn.extra_pages is not None
                else maybe_tvalue(0),
            }
        )
    if type_specific_subst is None:
        raise ValueError(f'Transaction object {txn} is invalid')

    fields_subst = (
        Subst({'TXID_CELL': KToken('"' + txid + '"', KSort('String'))})
        .compose(header_subst)
        .compose(type_specific_subst)
    )
    empty_array_fields_subst = Subst(
        {
            'ACCOUNTS_CELL': tvalue_list([]),
            'APPLICATIONARGS_CELL': tvalue_list([]),
            'FOREIGNAPPS_CELL': tvalue_list([]),
            'FOREIGNASSETS_CELL': tvalue_list([]),
            'TXNEXECUTIONCONTEXT_CELL': KToken('.K', KSort('K')),
        }
    )
    empty_pgm_fileds_subst = Subst(
        {
            'APPROVALPROGRAM_CELL': maybe_tvalue(None),
            'APPROVALPROGRAMSRC_CELL': KToken('int 0', KSort('TealInputPgm')),
            'CLEARSTATEPROGRAM_CELL': maybe_tvalue(None),
            'CLEARSTATEPROGRAMSRC_CELL': KToken('int 1', KSort('TealInputPgm')),
        }
    )
    empty_service_fields_subst = Subst(
        {'LOGDATA_CELL': tvalue_list([]), 'LOGSIZE_CELL': tvalue(0), 'TXSCRATCH_CELL': KApply('.Map')}
    )
    transaction_cell = fields_subst.apply(empty_transaction_cell)
    empty_fields_subst = Subst({k: maybe_tvalue(None) for k in free_vars(empty_transaction_cell)})

    return empty_fields_subst.compose(
        empty_service_fields_subst.compose(empty_array_fields_subst.compose(empty_pgm_fileds_subst))
    ).apply(transaction_cell)