#!/usr/bin/env python3
"""
Fetch option open-interest data into the CSV format oi_dayflip_share.html expects.

Two sources:

  1) ThetaData (historical, any date range; requires subscription + Theta Terminal running)
       python get_oi_csv.py thetadata GME 2024-05-01 2024-06-28 > gme_oi.csv

  2) CBOE delayed quotes (FREE, but today's snapshot only)
       python get_oi_csv.py cboe GME > gme_today.csv

Output columns: date,expiration,strike,right,open_interest[,spot]
No dependencies beyond the Python standard library.
"""
import csv, json, sys, time, urllib.request

THETA = "http://127.0.0.1:25510"   # Theta Terminal v2 default port


def http_json(url):
    with urllib.request.urlopen(url, timeout=60) as r:
        return json.loads(r.read().decode())


def fetch_thetadata(root, start, end, out):
    s8, e8 = start.replace("-", ""), end.replace("-", "")
    exps = http_json(f"{THETA}/v2/list/expirations?root={root}")["response"]
    exps = [str(e) for e in exps if str(e) >= s8]  # skip long-dead expirations
    w = csv.writer(out)
    w.writerow(["date", "expiration", "strike", "right", "open_interest"])
    n = 0
    for k, exp in enumerate(exps):
        url = (f"{THETA}/v2/bulk_hist/option/open_interest"
               f"?root={root}&exp={exp}&start_date={s8}&end_date={e8}")
        try:
            js = http_json(url)
        except Exception as ex:
            print(f"  skip {exp}: {ex}", file=sys.stderr)
            continue
        fmt = js.get("header", {}).get("format") or []
        try:
            i_oi, i_dt = fmt.index("open_interest"), fmt.index("date")
        except ValueError:
            i_oi, i_dt = 1, 2   # documented tick layout fallback
        for con in js.get("response", []):
            c = con.get("contract", {})
            K = c.get("strike", 0) / 1000.0
            r = str(c.get("right", ""))[:1].upper()
            ex8 = str(c.get("expiration", exp))
            e_iso = f"{ex8[:4]}-{ex8[4:6]}-{ex8[6:8]}"
            for t in con.get("ticks", []):
                oi = t[i_oi]
                if not oi:
                    continue
                d8 = str(t[i_dt])
                w.writerow([f"{d8[:4]}-{d8[4:6]}-{d8[6:8]}", e_iso, K, r, int(oi)])
                n += 1
        print(f"  [{k+1}/{len(exps)}] exp {exp}  rows so far {n}", file=sys.stderr)
        time.sleep(0.25)
    print(f"done: {n} rows", file=sys.stderr)


def fetch_cboe(root, out):
    js = http_json(f"https://cdn.cboe.com/api/global/delayed_quotes/options/{root.upper()}.json")
    data = js.get("data", {})
    spot = data.get("current_price") or data.get("close") or ""
    today = time.strftime("%Y-%m-%d")
    w = csv.writer(out)
    w.writerow(["date", "expiration", "strike", "right", "open_interest", "spot"])
    n = 0
    for o in data.get("options", []):
        sym = o.get("option", "")          # OCC: ROOT + YYMMDD + C/P + strike*1000 (8 digits)
        oi = o.get("open_interest", 0)
        if not oi or len(sym) < 15:
            continue
        tail = sym[-15:]
        yy, mm, dd, right, k8 = tail[:2], tail[2:4], tail[4:6], tail[6], tail[7:]
        try:
            K = int(k8) / 1000.0
        except ValueError:
            continue
        w.writerow([today, f"20{yy}-{mm}-{dd}", K, right, int(oi), spot])
        n += 1
    print(f"done: {n} rows (today's snapshot)", file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    mode, root = sys.argv[1].lower(), sys.argv[2].upper()
    if mode == "thetadata":
        if len(sys.argv) != 5:
            sys.exit("usage: get_oi_csv.py thetadata TICKER YYYY-MM-DD YYYY-MM-DD")
        fetch_thetadata(root, sys.argv[3], sys.argv[4], sys.stdout)
    elif mode == "cboe":
        fetch_cboe(root, sys.stdout)
    else:
        sys.exit("mode must be 'thetadata' or 'cboe'")
