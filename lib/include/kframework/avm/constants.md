# AVM Constants

These are taken from [here](https://developer.algorand.org/docs/get-details/parameter_tables)

```k
module AVM-CONSTANTS
  imports INT

  syntax Int ::= "PARAM_MIN_BALANCE"           [macro]
               | "PARAM_APP_PAGE_FLAT"         [macro]
               | "PARAM_APP_OPTIN_FLAT"        [macro]
               | "PARAM_MIN_BALANCE_PER_ENTRY" [macro]
               | "PARAM_UINT_MIN_BALANCE"      [macro]
               | "PARAM_BYTES_MIN_BALANCE"     [macro]
               | "PARAM_MIN_TXN_FEE"           [macro]
               | "PARAM_MAX_TXN_LIFE"          [macro]
```

Amount the min balance is set to by default, and amount it is increased by when creating or opting into
an ASA (MinBalance)

```k
  rule PARAM_MIN_BALANCE => 100000
```

Amount, per page, the min balance is increased by when creating an app (AppFlatParamsMinBalance)

```k
  rule PARAM_APP_PAGE_FLAT => 100000
```

Flat amount the min balance is increased by when opting into an app (AppFlatOptInMinBalance)

```k
  rule PARAM_APP_OPTIN_FLAT => 100000
```

Amount the min balance is increased per entry for local or global storage, regardless of type
(SchemaMinBalancePerEntry)

```k
  rule PARAM_MIN_BALANCE_PER_ENTRY => 25000
```

Additional amount the min balance is increased for local or global storage of ints (SchemaUintMinBalance)

```k
  rule PARAM_UINT_MIN_BALANCE => 3500
```

Additional amount the min balance is increased for local or global storage of byte strings
(SchemaBytesMinBalance)

```k
  rule PARAM_BYTES_MIN_BALANCE => 25000
```

Minimum transaction fee (MinTxnFee)

```k
  rule PARAM_MIN_TXN_FEE => 1000
```

Maximum transaction life (MaxTxnLife)

```k
  rule PARAM_MAX_TXN_LIFE => 1000
```

```k
endmodule
```