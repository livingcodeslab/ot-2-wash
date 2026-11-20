# Water checkout on November 20, 2026

The OT-2 completed the A1 rinse in 32 commands with zero reported errors. Water was visible in A1 after filling and in the waste lane after draining. The operator observed no spill. Volumes below are pipette commands. Recovery was assessed visually.

| Operation | Tip in bay 2 | Source → destination | Commanded volume |
| --- | --- | --- | --- |
| Prime | B1 | Bay 4 A1 → plate A1 | 200 µL |
| Wash | Same B1 | Bay 4 A1 → plate A1 | 200 µL |
| Rinse draw | Same B1 | Plate A1 → bay 3 A12 | 200 µL |
| Separate final draw | Fresh C1 | Center of plate A1 → bay 3 A12 | 200 µL aspiration setting |

## Setting the working height

The seated rim was 26.0 mm above the mounting reference. During the dry check the tip was visibly clear at 17.0 mm below the rim and bent at 18.0 mm. The robot lifted the tip, and the operator confirmed the plate stayed flat. The 17.5 mm midpoint served as the nominal well depth. The rinse tip worked at 16.7 mm below the rim.

For the follow-up draw, the operator confirmed the fresh C1 tip was straight and in the water at 17.0 mm below the rim. The robot aspirated at 12 µL/s, dispensed to A12 at 45 µL/s, discarded the tip and parked. A small amount remained near the rim and was left in place. The actual recovered volume was not measured.

## Code provenance

The [bench-tagged rinse file](https://github.com/livingcodeslab/ot-2-wash/blob/a1-rinse-bench-2026-11-20/ot2_biolite_24_water_rinse.py) has SHA-256 `068a76bc2f43d47ce71bf42730d1c4d4034b6990ce2e0c57e56c50ca576954ae`. The follow-up draw ran through supervised robot commands. The current importable protocol packages that sequence as an optional mode and has been tested in the offline simulator. A1 at 0 rpm was the only physical test location and speed.
