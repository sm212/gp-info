# Scraping NHS Choices

Python script to scrape information of GP practices from NHS choices.

Running `scraper.py` returns two csv's - `reviews.csv` and `key_info.csv`:

* `reviews.csv` contains every review, rating, reply, and dates for every GP practice.
* `key_info.csv` contains the number of patients, if the practice does evening & weekend appointments, the % of patients who would recommend the practice to friends & family, and the number of patients asked if they would recomment the practice to friends & family.

Practice IDs are included in both files to link on. Some practices have no reivews, so not every practice will be in `reviews.csv`.

There are ~10,000 practices, so the scraper takes a while to run (about 5 hours for me). The data is included in the repo for downloading. These csv's are the output of running the scraper on **January 5th 2020**.