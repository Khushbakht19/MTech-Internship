"""
gui package
------------------------------------------------------------------
Contains every visual component of Resume Screener Pro:

    - styles.py         : global ttk theme ("Emerald & Slate Professional")
    - splash_screen.py  : animated splash/loading screen
    - main_window.py     : root layout controller (sidebar + header + pages)
    - sidebar.py         : left navigation sidebar
    - header.py          : top header bar
    - dashboard.py       : Dashboard page
    - candidates.py      : Candidate Management page
    - jobs.py            : Job Management page
    - screening.py       : Resume Screening page
    - history.py         : Screening History page
    - analytics.py       : Analytics page
    - reports.py         : Reports page
    - about.py           : About page

Each page is a self-contained ttk.Frame subclass that receives the
shared DatabaseManager instance, so pages can read/write data
without ever touching SQL directly.
------------------------------------------------------------------
"""
