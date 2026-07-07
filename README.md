# OI Day-Flip Viewer — shareable edition

A single-file, no-install 3D viewer for option open-interest positioning.
Each trading day renders as a point-cloud "glyph"; play the days as a flipbook,
rotate the cloud, mirror calls/puts, quantize into pixel-art.

Ships with **synthetic demo data only** — this is a BYOD (bring-your-own-data) tool.

## Data policy — BYOD (Bring Your Own Data)

**Everything bundled here is synthetic.** The built-in demo day and `sample_data.csv`
are computer-generated for a fake ticker ("DEMO") — they exist only to show the
mechanics. No real market data is included because options data is licensed and
cannot be redistributed. You bring your own: fetch it with the included script
(ThetaData subscription, or the free CBOE daily snapshot) or export it from any
source you are licensed to use. Everything you load stays in your browser.


## Use it / deploy it (one click)

- **Just use it:** the live page is at `https://thegamestopsnow.github.io/oi-dayflip/` — nothing to install, drag your CSV on.
- **Your own copy on GitHub:** click **Use this template** at the top of this repo, name your copy, done — the included workflow auto-publishes it to `https://<your-username>.github.io/<repo-name>/` on the first push (if the badge stays gray, approve the workflow once under the Actions tab).
- **Other hosts:** [Deploy to Netlify](https://app.netlify.com/start/deploy?repository=https://github.com/TheGameStopsNow/oi-dayflip) · [Deploy with Vercel](https://vercel.com/new/clone?repository-url=https://github.com/TheGameStopsNow/oi-dayflip)
- **No host at all:** download the repo zip and double-click `index.html` — it runs from a local file.

## Quickstart

1. Open `index.html` in any browser (double-click works — no server needed).
2. Drag a CSV onto the page (or click **Load CSV…** next to the date dropdown).
   Try the included `sample_data.csv` first (5 days of a synthetic "DEMO" ticker with a
   mini gamma-ramp event on day 3 — fake data, safe to redistribute).
3. Press play. Drag to rotate, scroll to zoom. Click Top/Side/Front/Iso for preset views.

## CSV format

Header row required, columns in any order, case-insensitive:

| column        | required | accepted values                              |
|---------------|----------|----------------------------------------------|
| date          | yes      | 2024-05-16, 20240516, or 5/16/2024            |
| expiration    | yes      | same formats                                  |
| strike        | yes      | number (e.g. 20 or 22.5)                      |
| right         | yes      | C, CALL, P, PUT (only first letter is read)   |
| open_interest | yes      | integer > 0 (zero-OI rows can be omitted)     |
| spot          | no       | underlying close; enables moneyness Y-axis.   |
|               |          | If missing, the OI-median strike is used.     |

One underlying per CSV. One row per contract per day. Multiple days in one file
make a flipbook; you can also drop several CSVs at once and they merge.
Alternate header names are recognized (`oi`, `exp`, `type`, `underlying_price`, …).

## Where to get data

**ThetaData** (https://thetadata.net) — full OI history, any US optionable ticker.
Needs their options subscription and the Theta Terminal app running locally, then:

    python get_oi_csv.py thetadata GME 2024-05-01 2024-06-28 > gme_oi.csv

**CBOE delayed quotes** — free, no signup, but *today's snapshot only*:

    python get_oi_csv.py cboe GME > gme_today.csv

Run it daily (cron it) and you grow a history for free.

**Broker/vendor exports** — anything (ORATS, ivolatility, your broker's chain
export) works if you reshape it to the columns above.

Note: open interest is per-day data published each morning for the prior session —
there is no intraday OI.

## Troubleshooting

- "missing column(s)" toast → rename your header per the table above.
- Nothing renders → check rows have OI > 0 and dates parsed (toast shows the range loaded).
- Huge files: ~50 MB / a few hundred days per file is comfortable; split bigger ranges.
- The viewer never uploads anything — all parsing happens in your browser.

## Credit

Built by TheGameStopsNow. Share freely.
