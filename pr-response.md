# PR Response Doc — CineLog Watchlist Feature

## AI Usage

I used Codex to help orient me to the repository, inspect the six review comments, and stress-test the reasoning behind the design decisions. I verified every suggested change against the source code and test suite before keeping it.

## Comment 1 — Rename

**What I did:** Renamed `save_to_watchlist()` to `add_to_watchlist()` in `services/watchlist_service.py` and updated its import and call site in `routes/watchlist/watchlist.py`.

**How I verified:** Searched the whole repository for `save_to_watchlist` and confirmed that no call sites remain. I also ran the full test suite.

## Comment 2 — Deduplication

**What I did:** Added an `AlreadyInWatchlistError` and made `add_to_watchlist()` query for an existing entry with the same `user_id` and `film_id` before inserting. If one exists, the service raises the domain-specific error and does not commit another row. This follows the established `add_to_collection()` pattern.

**How I verified:** Added the same film twice in an isolated test database, confirmed the second call raises `AlreadyInWatchlistError`, and confirmed only one matching row remains. I also ran the full test suite.

## Comment 3 — Missing test

**What I did:** Created `tests/test_watchlist.py` using the same in-memory app, fixture, and `pytest.raises` structure as `tests/test_collection.py`. The requested test calls `add_to_watchlist()` with an ID that is absent from the database and expects `FilmNotFoundError`. I also included a focused regression test for the deduplication behavior from Comment 2.

**How I verified:** Ran `pytest tests/test_watchlist.py -v` and then `pytest tests/ -v`; both the new tests and the existing collection tests pass.

## Comment 4 — Default visibility

**My position:**

**Reasoning:**

**Tradeoff acknowledged:**

## Comment 5 — Sort order

**My position:**

**Reasoning:**

**Engagement with reviewer's point:**

## Comment 6 — Rebase

**What conflicted:**

**How I resolved it:**

**How I verified no conflict remains:**

## PR Description

To be completed after all review comments are addressed.
