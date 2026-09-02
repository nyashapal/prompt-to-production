\# UC-0C Budget Growth Calculator Skills



skills:



&#x20; - name: load\_dataset

&#x20;   description: >

&#x20;     Reads the municipal budget CSV, validates the required columns, and

&#x20;     identifies null actual\_spend values and their recorded reasons.



&#x20;   input: >

&#x20;     A CSV file path containing period, ward, category, budgeted\_amount,

&#x20;     actual\_spend, and notes columns.



&#x20;   output: >

&#x20;     A validated collection of budget rows together with null-row information.



&#x20;   error\_handling: >

&#x20;     If the file cannot be read or required columns are missing, fail clearly

&#x20;     instead of producing a calculation from incomplete data.



&#x20; - name: compute\_growth

&#x20;   description: >

&#x20;     Calculates growth for one explicitly requested ward and category using

&#x20;     the explicitly requested growth type and returns one row per period.



&#x20;   input: >

&#x20;     Validated budget rows, one ward, one category, and an explicit growth

&#x20;     type such as MoM.



&#x20;   output: >

&#x20;     A per-period table containing the period, actual spend, growth result,

&#x20;     formula used, and any null-data flag or reason.



&#x20;   error\_handling: >

&#x20;     Refuse missing or unsupported growth types, missing wards or categories,

&#x20;     cross-ward or cross-category aggregation, and do not calculate growth

&#x20;     when current or previous actual\_spend is null.

