This directory contains code files to

1. Scrape Publishers Marketplace for relevant bestseller lists (scrape_bestsellers.py)
2. Concatenate resulting lists and remove duplicate entries (combine_book_lists_single_year.py, combine_book_lists_over_years.py, remove_duplicate_rows.py)
3. Fetch metadata about books on these lists from Google Books and SuperSummary (fetch_book_metadata.py, fetch_book_summaries.py)
4. Query an LLM to extract character professions from the books (fetch_book_data.py)
5. Get a test and validation set of books (get_validation_set.py)
6. Plot various properties for the files (plot_*.py)

All code files are in the scripts subdirectory, with the exception of a configuration file called config.py.

The directory also contains some resulting data in the data subdirectory, of which the main file is book_character_professions.csv. This file contains the result of querying an LLM to extract character professions.

Resulting plots are contained in the plots subdirectory.

Note that some raw data have been removed, namely the results from scraping Publishers Marketplace. (In compliance with their terms of service.) There are thus some scripts which point to non-existent files.