"""Supervised water rinse for an empty BioLite 24-well plate.

Select "Final drain only" for the separate center draw from an already rinsed
well A1 on the stationary shaker. Use a fresh C1 tip and enter the deepest
clear working position verified for that setup, measured below the A1 rim.
Bay 3 lane A12 must have room for another 200 uL. This mode adds no water.

Match the deck before running:
    2   Open Opentrons OT-2 200 uL filter tip rack. Start at A1, or select
        "A1 tip already used" to start at B1 after a dry check. A whole-plate
        run uses 24 consecutive fresh tips, down each column in turn.
    3   NEST 12-channel 15 mL reservoir. Leave lane 12 (A12) empty for waste.
    4   NEST 12-channel 15 mL reservoir. Use only lane 1 (A1) for plain water.
        Start with at least 2.4 mL in that lane for the A1 test, or 11.6 mL for
        all 24 wells. These starting volumes include a 2 mL reserve.
    5   BioLite on deck, only if Deck slot 5 is selected.
    6   Parked tall 1,000 uL filter tip rack, lid off. Its height is included
        in travel planning. All tip pickups are from bay 2.
    9   Idle Temperature Module GEN2, unloaded.
    10  Idle Heater-Shaker. For shaker placement, fit the Opentrons 96 Flat
        Bottom Heater-Shaker Adapter (991-00065) and your seated BioLite.
    11  Clear the slot beside the Heater-Shaker for latch clearance.
    12  Fixed trash. Clear other unused labware and cables from the travel path.

Use a dry, empty, lidless plate with A1 at the back left. In the App, select
placement and enter the measured well depth (rim to inside floor). On the
shaker also enter the assembled height from the adapter's lower mounting
face to the well rim with the plate fully seated. Measure that height as a
stack, including the holder. The plate's deck-alone height is not the stack
height. The A1 coordinates come from the November 17 BioLite checkout.

For all 24 wells, also measure the center-to-center distances A1 to A6 and
A1 to D1. Start with A1 only and run Labware Position Check for this
placement before starting. Use the water test with the calibrated right
P300 Single-Channel GEN2 and its 200 uL filter-tip length calibration.

Each dry well first receives 200 uL of starting water. The wash then adds
200 uL and removes 200 uL to bay 3 A12. This leaves about 200 uL covering
the well floor. One fresh tip is used per well. The plate stays stationary. The shaker-mode latch
closes at run time after the setup pause. The protocol has no rail-light,
heating, or shake commands. Import to review the setup without starting
a run, since the OT-2 may home when a run starts.
"""

from opentrons import protocol_api


metadata = {
    "protocolName": "BioLite 24-well | 200 uL rinse | tips in bay 2",
    "description": "Right P300. Water from bay 4 A1, waste to bay 3 A12. Stationary plate.",
}
requirements = {"robotType": "OT-2", "apiLevel": "2.19"}

PLATE_WIDTH_MM = 127.6
PLATE_LENGTH_MM = 85.4
DECK_RIM_MM = 20.3
A1_FROM_LEFT_MM = 15.0
A1_FROM_BACK_MM = 12.0
WELL_DIAMETER_MM = 15.6

STARTING_WATER_UL = 200
WASH_UL = 200
SOURCE_RESERVE_UL = 2000


def add_parameters(parameters):
    parameters.add_bool(
        variable_name="final_drain_only",
        display_name="Final drain only",
        description="Draw residual water from plate A1 using a fresh C1 tip in bay 2.",
        default=False,
    )
    parameters.add_float(
        variable_name="final_drain_mm",
        display_name="Final depth below rim",
        description="Final drain only. Enter the depth verified clear with a straight tip in A1.",
        default=0.0, minimum=0.0, maximum=DECK_RIM_MM, unit="mm",
    )
    parameters.add_str(
        variable_name="placement",
        display_name="Plate placement",
        description="Use the 96 Flat Bottom Heater-Shaker holder, or put the plate directly in bay 5.",
        choices=[
            {"display_name": "Heater-Shaker 10", "value": "shaker"},
            {"display_name": "Deck slot 5", "value": "deck"},
        ],
        default="shaker",
    )
    parameters.add_bool(
        variable_name="whole_plate",
        display_name="All 24 wells",
        description="Off is an A1-only checkout. On requires both measured well spans and 24 fresh tips.",
        default=False,
    )
    parameters.add_bool(
        variable_name="a1_tip_used",
        display_name="A1 tip already used",
        description="Use the next fresh tip, B1 in bay 2, if A1 was consumed for a dry height check.",
        default=False,
    )
    parameters.add_float(
        variable_name="depth_mm",
        display_name="Well depth",
        description="Enter rim to inside floor. Zero displays setup only.",
        default=0.0,
        minimum=0.0,
        maximum=DECK_RIM_MM,
        unit="mm",
    )
    parameters.add_float(
        variable_name="stack_rim_mm",
        display_name="Stacked rim height",
        description="On shaker only. Measure from the holder's lower mounting face to the well rim.",
        default=0.0,
        minimum=0.0,
        maximum=40.0,
        unit="mm",
    )
    parameters.add_float(
        variable_name="span_x_mm",
        display_name="A1 to A6 span",
        description="For all 24 wells. Measure the center-to-center horizontal distance.",
        default=0.0,
        minimum=0.0,
        maximum=105.0,
        unit="mm",
    )
    parameters.add_float(
        variable_name="span_y_mm",
        display_name="A1 to D1 span",
        description="For all 24 wells. Measure the center-to-center front-to-back distance.",
        default=0.0,
        minimum=0.0,
        maximum=67.0,
        unit="mm",
    )


def plate_definition(rim_mm, depth_mm, span_x_mm, span_y_mm, placement, whole_plate):
    """Use the same module reference plane as an Opentrons combined adapter definition."""
    columns = 6 if whole_plate else 1
    rows = "ABCD" if whole_plate else "A"
    ordering = [[f"{row}{column}" for row in rows] for column in range(1, columns + 1)]
    radius = WELL_DIAMETER_MM / 2
    if whole_plate and (
        span_x_mm / 5 <= WELL_DIAMETER_MM or span_y_mm / 3 <= WELL_DIAMETER_MM
        or A1_FROM_LEFT_MM + span_x_mm + radius > PLATE_WIDTH_MM
        or A1_FROM_BACK_MM + span_y_mm + radius > PLATE_LENGTH_MM
    ):
        raise ValueError("Check the measured A1 to A6 and A1 to D1 center distances.")

    wells = {}
    for column_index, column in enumerate(ordering):
        for row_index, well_name in enumerate(column):
            wells[well_name] = {
                "shape": "circular",
                "diameter": WELL_DIAMETER_MM,
                "depth": depth_mm,
                "totalLiquidVolume": 1000,
                "x": A1_FROM_LEFT_MM + column_index * span_x_mm / 5,
                "y": PLATE_LENGTH_MM - A1_FROM_BACK_MM - row_index * span_y_mm / 3,
                "z": rim_mm - depth_mm,
            }

    # A new measurement produces a new definition identity for position offsets.
    geometry_id = "_".join(
        str(round(100 * v)) for v in (rim_mm, depth_mm, span_x_mm, span_y_mm)
    )
    label = "BioLite 24-well"
    if placement == "shaker":
        label += " with 96 Flat Bottom Heater-Shaker Adapter"
    return {
        "schemaVersion": 2,
        "namespace": "custom_beta",
        "version": 1,
        "brand": {"brand": "Thermo Scientific", "brandId": ["930186"]},
        "metadata": {
            "displayName": label,
            "displayCategory": "wellPlate",
            "displayVolumeUnits": "mL",
            "tags": [],
        },
        "parameters": {
            "format": "irregular",
            "isTiprack": False,
            "isMagneticModuleCompatible": False,
            "loadName": f"biolite_24_{placement}_{len(wells)}_{geometry_id}",
        },
        "dimensions": {
            "xDimension": PLATE_WIDTH_MM,
            "yDimension": PLATE_LENGTH_MM,
            "zDimension": rim_mm,
        },
        "cornerOffsetFromSlot": {"x": 0, "y": 0, "z": 0},
        "ordering": ordering,
        "groups": [{
            "wells": list(wells),
            "metadata": {"wellBottomShape": "flat"},
        }],
        "wells": wells,
    }


def confirm_shaker_idle(shaker):
    if shaker.current_speed != 0 or shaker.target_speed not in (None, 0):
        raise RuntimeError("Stop the Heater-Shaker and verify 0 rpm before pipetting.")
    if shaker.target_temperature is not None:
        raise RuntimeError("Deactivate Heater-Shaker heating before the water checkout.")


def drain_remaining_a1(protocol, p300, well, waste, depth_below_rim):
    p300.pick_up_tip()
    p300.move_to(well.top(z=7), speed=38)
    protocol.pause("Confirm a straight tip is centered over the remaining water in A1.")
    p300.prepare_to_aspirate()
    target = well.top(z=-depth_below_rim)
    p300.move_to(target, speed=6, force_direct=True)
    protocol.pause("Resume only if the tip is straight and its opening is in the water.")
    p300.flow_rate.aspirate = 12
    p300.flow_rate.dispense = 45
    p300.aspirate(WASH_UL, target)
    protocol.delay(seconds=1)
    p300.move_to(well.top(z=7), speed=12, force_direct=True)
    p300.dispense(WASH_UL, waste)
    p300.drop_tip()
    protocol.home()


def run(protocol: protocol_api.ProtocolContext):
    params = protocol.params
    on_shaker = params.placement == "shaker"
    shaker = protocol.load_module("heaterShakerModuleV1", "10")
    protocol.load_module("temperature module gen2", "9")
    waste_reservoir = protocol.load_labware("nest_12_reservoir_15ml", "3", label="Waste reservoir")
    water_reservoir = protocol.load_labware("nest_12_reservoir_15ml", "4", label="Water reservoir")
    tips = protocol.load_labware("opentrons_96_filtertiprack_200ul", "2")
    protocol.load_labware("opentrons_96_filtertiprack_1000ul", "6", label="Parked tall tip rack")
    p300 = protocol.load_instrument("p300_single_gen2", "right", tip_racks=[tips])
    first_tip_name = "B1" if params.a1_tip_used else "A1"
    if params.final_drain_only:
        if not on_shaker or params.whole_plate:
            raise ValueError("Select Heater-Shaker 10 and A1 only for the final drain.")
        first_tip_name = "C1"
    first_tip = tips[first_tip_name]
    p300.starting_tip = first_tip

    depth = params.depth_mm
    stacked_rim = params.stack_rim_mm
    rim = stacked_rim if on_shaker else DECK_RIM_MM
    missing_measurement = depth == 0 or (on_shaker and stacked_rim == 0)
    if missing_measurement:
        protocol.comment(
            "Setup only. Enter the measured well depth. For shaker placement also "
            "enter the holder-plus-plate rim height to generate the rinse steps."
        )
        return
    if not 5 <= depth <= min(DECK_RIM_MM - 0.5, rim - 0.5):
        raise ValueError("Recheck the measured well depth and seated rim height.")
    if params.final_drain_only and not 0 < params.final_drain_mm < depth:
        raise ValueError("Enter a verified final drain depth above the A1 floor.")

    whole_plate = params.whole_plate
    span_x = params.span_x_mm if whole_plate else 0
    span_y = params.span_y_mm if whole_plate else 0
    definition = plate_definition(rim, depth, span_x, span_y, params.placement, whole_plate)
    if on_shaker:
        plate = shaker.load_labware_from_definition(definition)
        holder_check = "Check the fitted 96 Flat Bottom holder and that the plate is seated firmly."
    else:
        plate = protocol.load_labware_from_definition(definition, "5")
        holder_check = "Check that the plate is seated flat in bay 5."

    source = water_reservoir["A1"].bottom(z=2)
    waste = waste_reservoir["A12"].top(z=-3)
    water_per_well = STARTING_WATER_UL + WASH_UL
    minimum_water_ml = (water_per_well * len(plate.wells()) + SOURCE_RESERVE_UL) / 1000
    setup = (
        f"{holder_check} Verify A1 is back left, the plate is dry and the lids are off. "
        f"Check the right P300 and a fresh 200 uL filter tip at {first_tip_name} in bay 2. "
        "Verify both open reservoirs match NEST 360102. "
        f"Bay 4 lane 1 (A1) needs at least {minimum_water_ml:g} mL water. "
        "Leave bay 3 lane 12 (A12) empty for waste. Keep bay 11 clear beside the shaker. "
        "Clear other unused labware and cables from the travel path. Keep both modules idle."
    )
    if params.final_drain_only:
        setup = (
            f"{holder_check} Confirm water remains in open plate A1, a fresh C1 tip "
            "is in bay 2, and open waste lane A12 in bay 3 has room for 200 uL. "
            "Keep bay 11 clear and both modules idle."
        )
    protocol.pause(setup)
    confirm_shaker_idle(shaker)
    if on_shaker:
        shaker.close_labware_latch()
        protocol.pause("Check the closed latch and confirm the plate is stable at 0 rpm.")
        confirm_shaker_idle(shaker)

    p300.move_to(first_tip.top(z=12), speed=40)
    protocol.pause(f"Check that the right P300 is centered over a fresh {first_tip_name} tip in bay 2.")

    if params.final_drain_only:
        confirm_shaker_idle(shaker)
        drain_remaining_a1(protocol, p300, plate["A1"], waste, params.final_drain_mm)
        return

    for index, well in enumerate(plate.wells()):
        p300.pick_up_tip()
        if index == 0:
            check_wells = ("A6", "D6", "D1", "A1") if whole_plate else ("A1",)
            for name in check_wells:
                p300.move_to(plate[name].top(z=10), speed=30)
                protocol.pause(f"Check the dry tip is straight and centered over {name}.")
            p300.move_to(well.bottom(z=2.0), speed=18, force_direct=True)
            protocol.pause(
                "Check the dry tip is centered and about 2 mm above the inside floor of A1. "
                "Stop and recheck the geometry if the gap or centering is off."
            )

        # Both dispenses are near the rim, above the water. The tip returns
        # to the reservoir only before it has contacted liquid in a plate well.
        for volume in (STARTING_WATER_UL, WASH_UL):
            p300.aspirate(volume, source, rate=0.30)
            p300.dispense(volume, well.top(z=-2), rate=0.25)
        protocol.delay(seconds=2, msg="Let the water settle.")
        if index == 0:
            p300.move_to(well.top(z=10), speed=25, force_direct=True)
            protocol.pause("Check that both 200 uL additions landed in A1 before draining 200 uL.")
            confirm_shaker_idle(shaker)

        drain = well.bottom(z=0.8)
        p300.move_to(drain, speed=18, force_direct=True)
        p300.aspirate(WASH_UL, drain, rate=0.20)
        p300.dispense(WASH_UL, waste, rate=0.35)
        p300.drop_tip()
        if index == 0 and whole_plate:
            protocol.pause("Check the A1 drain and remaining water before rinsing the other wells.")
            confirm_shaker_idle(shaker)

    protocol.comment(
        f"Water checkout finished for {len(plate.wells())} well(s). "
        f"Each well received a {WASH_UL} uL wash and retains about {STARTING_WATER_UL} uL."
    )
