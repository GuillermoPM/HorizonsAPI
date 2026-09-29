"""
Horizons API to download orbital data from JPL Horizons system.
"""
import csv
import io

import pandas as pd
import requests

VECTOR_COLUMNS = ["x", "y", "z", "vx", "vy", "vz"]


class HorizonsAPI:
    """
    A class to interact with the JPL Horizons system for downloading orbital data.
    """

    def __init__(self, base_url: str = "https://ssd.jpl.nasa.gov/api/horizons.api"):
        """
        Initializes the HorizonsAPI with a base URL.

        :parameter: base_url: The base URL for the JPL Horizons API.
        """
        self.base_url = base_url

    def get_orbital_data(self, query: dict) -> str:
        """
        Sends a query to the Horizons API and returns the raw ephemeris text.

        :parameter: query: Horizons parameters (e.g. COMMAND, START_TIME, STOP_TIME, STEP_SIZE).
            Values are quoted automatically as the API requires.

        :returns: The ephemeris text returned by Horizons (the 'result' field of the JSON response).
        """
        params = {key: f"'{value}'" for key, value in query.items() if value is not None}
        params["format"] = "json"

        response = requests.get(self.base_url, params=params, timeout=60)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()

        if "error" in data:
            raise RuntimeError(f"Horizons API error: {data['error']}")

        result = data["result"]
        if "$$SOE" not in result:
            raise RuntimeError(f"Horizons returned no ephemeris data:\n{result}")
        return result

    @staticmethod
    def parse_vectors_csv(result: str) -> pd.DataFrame:
        """
        Parses a VECTORS ephemeris (CSV_FORMAT=YES, VEC_TABLE=2) into a dataframe.

        :parameter: result: The ephemeris text returned by get_orbital_data.

        :returns: pd.DataFrame with columns ['utc', 'x', 'y', 'z', 'vx', 'vy', 'vz'].
        """
        block = result.split("$$SOE", 1)[1].split("$$EOE", 1)[0]
        rows = []
        for row in csv.reader(io.StringIO(block.strip()), skipinitialspace=True):
            if not row:
                continue
            # Columns: JD, calendar date, X, Y, Z, VX, VY, VZ, (trailing empty field)
            date = row[1].replace("A.D.", "").strip()
            rows.append([date] + [float(value) for value in row[2:8]])

        df = pd.DataFrame(rows, columns=["utc"] + VECTOR_COLUMNS)
        df["utc"] = pd.to_datetime(df["utc"], format="%Y-%b-%d %H:%M:%S.%f")
        return df