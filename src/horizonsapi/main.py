from .horizon_api import HorizonsAPI 
import argparse

def main():
    argument_parser = argparse.ArgumentParser(description="Fetch orbital data from JPL Horizons.")
    argument_parser.add_argument("--target", required=True, help="The name or ID of the celestial body (e.g. -155 for KPLO).")
    argument_parser.add_argument("--start_date", required=True, help="The start time for the data retrieval (e.g. '2024-01-01').")
    argument_parser.add_argument("--end_date", required=True, help="The end time for the data retrieval (e.g. '2024-01-02').")
    argument_parser.add_argument("--step_size", required=True, help="The time step size for the data points (e.g. '1 m', '10 m', '1 h').")
    argument_parser.add_argument("--center", default="@301",
                                 help="Coordinate center (default: @301, Moon center).")
    argument_parser.add_argument("--ephem-type", default="VECTORS",
                                 choices=["VECTORS", "ELEMENTS", "OBSERVER"],
                                 help="Ephemeris type (default: VECTORS).")
    argument_parser.add_argument("--ref-plane", default="FRAME",
                                 choices=["FRAME", "ECLIPTIC", "BODY EQUATOR"],
                                 help="Reference plane (default: FRAME, ICRF equator).")
    argument_parser.add_argument("--ref-system", default="ICRF",
                                 choices=["ICRF", "B1950"],
                                 help="Reference system (default: ICRF).")
    argument_parser.add_argument("--out-units", default="KM-S",
                                 choices=["KM-S", "AU-D", "KM-D"],
                                 help="Output units (default: KM-S).")
    argument_parser.add_argument("--vec-table", default="2",
                                 help="Vector table content (default: 2, position and velocity only).")
    argument_parser.add_argument("--time-type", default="UT",
                                 choices=["TDB", "TT", "UT"],
                                 help="Time scale for input/output epochs (default: TDB).")
    argument_parser.add_argument("--no-csv", action="store_true",
                                 help="Disable CSV output format.")
    argument_parser.add_argument("--output", "-o",
                                 help="Output file. Parsed to a utc,x,y,z,vx,vy,vz CSV for VECTORS/table 2 "
                                      "in CSV format; otherwise the raw Horizons text is written. "
                                      "Printed to stdout if omitted.")
    args = argument_parser.parse_args()

    horizons_api = HorizonsAPI()
    query_params = {
        "COMMAND": args.target,
        "OBJ_DATA": "NO",
        "MAKE_EPHEM": "YES",
        "START_TIME": args.start_date,
        "STOP_TIME": args.end_date,
        "STEP_SIZE": args.step_size,
        "CENTER": args.center,
        "EPHEM_TYPE": args.ephem_type,
        "REF_PLANE": args.ref_plane,
        "REF_SYSTEM": args.ref_system,
        "OUT_UNITS": args.out_units,
        "VEC_TABLE": args.vec_table,
        "TIME_TYPE": args.time_type,
        "CSV_FORMAT": "NO" if args.no_csv else "YES",
    }
    result = horizons_api.get_orbital_data(query_params)

    parseable = args.ephem_type == "VECTORS" and args.vec_table == "2" and not args.no_csv
    if parseable:
        df = horizons_api.parse_vectors_csv(result)
        if args.output:
            df.to_csv(args.output, index=False)
            print(f"Wrote {len(df)} states to {args.output}")
        else:
            print(df.to_csv(index=False))
    elif args.output:
        with open(args.output, "w") as f:
            f.write(result)
        print(f"Wrote raw Horizons output to {args.output}")
    else:
        print(result)

    


if __name__ == "__main__":
    main()