# OT-2 water wash for a BioLite 24-well plate

Use a right-mounted P300 Single-Channel GEN2 with 200 µL filter tips to rinse a well while the plate stays on a stationary Heater-Shaker. The protocol runs on the OT-2 using Opentrons Python API 2.19. The lab's separate [heater-shaker controller](https://github.com/livingcodeslab/ot-2-shake) handles standalone USB module operation.

## Deck setup

| Bay | Item | Setup |
| --- | --- | --- |
| 2 | Opentrons 200 µL filter tips | Remove lid. A1 is back left. The rinse begins at A1, or B1 if A1 was used for the dry check. The final draw uses C1. |
| 3 | NEST 360102 12-lane reservoir | A12, rightmost lane, receives waste. Start the rinse with this lane empty. |
| 4 | NEST 360102 12-lane reservoir | A1, leftmost lane, holds water. Load at least 2.4 mL for one dry well. |
| 6 | Parked 1000 µL filter tip rack | The protocol includes the taller rack in its travel calculations. |
| 9 | Temperature Module GEN2 | Idle and unloaded. |
| 10 | Heater-Shaker with Opentrons 96 Flat Bottom Adapter 991-00065 | Seat the lidless Thermo Scientific BioLite 930186 plate with A1 at back left. Keep the shaker at 0 rpm and heating off. |
| 11 and 12 | Latch clearance and fixed trash | Keep bay 11 clear and the trash opening accessible. |

## Run a single well

1. Download [the Python protocol](./ot2_biolite_24_water_rinse.py) and import it into the Opentrons App. Use the calibrated P300 and the matching 200 µL tip length calibration.
2. Select **Heater-Shaker 10** and leave **All 24 wells** off. Enter the well depth and the height from the adapter’s bottom mounting face to the seated well rim. Leaving the geometry at zero gives a setup-only preview. Run Labware Position Check for this placement.
3. For a dry well, leave **Final drain only** off. Select **A1 tip already used** if the dry check consumed A1. The program primes with 200 µL of water, adds the 200 µL wash, and draws 200 µL into waste. The nominal remainder is 200 µL.
4. To draw the remaining pool, start a **separate run** with **Final drain only** on. Leave the plate seated, supply a fresh C1 tip, and enter the center depth verified clear on this setup in **Final depth below rim**. Resume the final aspiration only when the straight tip opening is in the water. A center draw can leave water near the rim.

The November 20 A1 checkout used a 26.0 mm seated rim height, an estimated 17.5 mm well depth, a 16.7 mm rinse draw and a separate 17.0 mm final draw below the rim. Recheck the geometry when the plate, adapter or position changes. See the [bench record](docs/bench-results.md) for how these values were obtained.

The rinse also accepts a plate on deck in bay 5. The whole-plate option requires measured A1–A6 and A1–D1 center distances, 24 consecutive fresh tips, and at least 11.6 mL in the source lane. Physical testing covered A1 on the stationary shaker.

## Offline tests

From the repository root in a Python 3.12 virtual environment, run:

```sh
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

The simulator checks the setup-only default, the single-well rinse, and the separate final draw. The test suite runs without connecting to a robot.
