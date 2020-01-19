# Scraping NHS Choices

Python script to scrape information of GP practices from NHS choices.

Running `scraper.py` returns two csv's - `reviews.csv` and `key_info.csv`:

* `reviews.csv` contains every review, review date, rating, reply, and reply date for every GP practice.
* `key_info.csv` contains the number of patients, if the practice does evening & weekend appointments, the % of patients who would recommend the practice to friends & family, and the number of patients asked if they would recommend the practice to friends & family. It also contains practice address, which should let you link to other NHS Digital datasets if you want.

Practice IDs are included in both files to link on. Some practices have no reviews, so not every practice will be in `reviews.csv`.

There are thousands of practices, so the scraper takes a while to run (about 5 hours for me). The data is included in the repo for downloading.

The csv's in this repo are the output of running the scraper on **January 19th 2020**. There are **85,120** reviews for **9,094** GP practices.