import requests

# Celestrak ISS TLE source
URL = "https://celestrak.org/NORAD/elements/gp.php?CATNR=25544&FORMAT=TLE"

def fetch_iss_tle():
    print("📡 Fetching ISS TLE data...")

    r = requests.get(URL, timeout=10)

    if r.status_code != 200:
        print("❌ Error: Unable to fetch TLE")
        return None

    tle = r.text.strip().splitlines()

    if len(tle) < 3:
        print("❌ Invalid TLE data received")
        return None

    name = tle[0].strip()
    line1 = tle[1].strip()
    line2 = tle[2].strip()

    print("✅ TLE Fetched Successfully\n")
    print(name)
    print(line1)
    print(line2)

    return name, line1, line2


if __name__ == "__main__":
    fetch_iss_tle()
