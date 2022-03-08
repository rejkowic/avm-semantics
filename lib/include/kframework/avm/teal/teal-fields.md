TEAL Fields
===========

TEAL fields refer to names of TEAL opcode immediate arguments. Unlike TEAL
constants, TEAL fields cannot appear as arguments to the `int` psuedo-op;
rather, they can only appear as arguments to their corresponding opcode.

```k
module TEAL-FIELDS
  import TEAL-TYPES-SYNTAX
```

## `global` Fields

```k
  syntax GlobalField ::= "MinTxnFee"
                       | "MinBalance"
                       | "MaxTxnLife"
                       | "ZeroAddress"
                       | "GroupSize"
                       | "LogicSigVersion"
                       | "Round"
                       | "LatestTimestamp"
                       | "CurrentApplicationID"
                       | "CurrentApplicationAddress"
```

## Asset Fields

### `asset_holding_get` Fields

```k
  syntax AssetHoldingField ::= "AssetBalance"
                             | "AssetFrozen"
```

### `asset_params_get` Fields

```k
  syntax AssetParamsField ::= "AssetTotal" [klabel(AssetTotal), symbol]
                            | "AssetDecimals" [klabel(AssetDecimals), symbol]
                            | "AssetDefaultFrozen" [klabel(AssetDefaultFrozen), symbol]
                            | "AssetUnitName" [klabel(AssetUnitName), symbol]
                            | "AssetName" [klabel(AssetName), symbol]
                            | "AssetURL" [klabel(AssetURL), symbol]
                            | "AssetMetadataHash" [klabel(AssetMetadataHash), symbol]
                            | "AssetManager" [klabel(AssetManager), symbol]
                            | "AssetReserve" [klabel(AssetReserve), symbol]
                            | "AssetFreeze" [klabel(AssetFreeze), symbol]
                            | "AssetClawback" [klabel(AssetClawback), symbol]
```

## Transaction Fields

### `txn`/`gtxn` fields

```k
  syntax TxnField ::= TxnHeaderField
                    | TxnPayField
                    | TxnKeyregField
                    | TxnAcfgField
                    | TxnAxferField
                    | TxnAfrzField
                    | TxnApplField

  syntax TxnHeaderField ::= "TxID"
                          | "Sender"
                          | "Fee"
                          | "FirstValid"
                          | "FirstValidTime"
                          | "LastValid"
                          | "Note"
                          | "Lease"
                          | "RekeyTo"
                          | "TxType"
                          | "TypeEnum"
                          | "GroupIndex"

  syntax TxnPayField    ::= "Receiver"
                          | "Amount"
                          | "CloseRemainderTo"

  syntax TxnKeyregField ::= "votePK"
                          | "SelectionPK"
                          | "VoteFirst"
                          | "VoteLast"
                          | "VoteKeyDilution"

  syntax TxnAcfgField   ::= "ConfigAsset"
                          | "ConfigAssetTotal"
                          | "ConfigAssetDecimals"
                          | "ConfigAssetDefaultFrozen"
                          | "ConfigAssetUnitName"
                          | "ConfigAssetName"
                          | "ConfigAssetURL"
                          | "ConfigAssetMetaDataHash"
                          | "ConfigAssetManager"
                          | "ConfigAssetReserve"
                          | "ConfigAssetFreeze"
                          | "ConfigAssetClawback"

  syntax TxnAxferField  ::= "XferAsset"
                          | "AssetAmount"
                          | "AssetASender"
                          | "AssetReceiver"
                          | "AssetCloseTo"

  syntax TxnAfrzField   ::= "FreezeAsset"
                          | "FreezeAssetAccount"
                          | "FreezeAssetFrozen"

  syntax TxnApplField   ::= "ApplicationID"
                          | "OnCompletion"
                          | "NumAppArgs"
                          | "NumAccounts"
                          | "ApprovalProgram"
                          | "ClearStateProgram"
```

### `txna`/`gtxna` fields

```k
  syntax TxnaField ::= "ApplicationArgs"
                     | "Accounts"

  syntax TxnaFieldExt ::= TxnaField
                        | "ForeignApps"
                        | "ForeignAssets"
```

```k
endmodule
```