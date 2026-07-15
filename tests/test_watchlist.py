"""Tests for the watchlist service."""

from datetime import datetime, timedelta, timezone

import pytest

from app import create_app, db
from models import Film, User, WatchlistEntry
from services.collection_service import FilmNotFoundError
from services.watchlist_service import (
    AlreadyInWatchlistError,
    add_to_watchlist,
    get_watchlist,
)


@pytest.fixture
def app():
    """Create an isolated test app with an in-memory database."""
    app = create_app(config={
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def sample_user(app):
    """Create a user for watchlist tests."""
    with app.app_context():
        user = User(username="watcher", email="watcher@example.com")
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture
def sample_film(app):
    """Create a film for watchlist tests."""
    with app.app_context():
        film = Film(title="Moonlight", year=2016, genre="Drama")
        db.session.add(film)
        db.session.commit()
        return film.id


def test_add_to_watchlist_nonexistent_film_raises(app, sample_user):
    """Adding a nonexistent film should raise FilmNotFoundError."""
    with app.app_context():
        with pytest.raises(FilmNotFoundError):
            add_to_watchlist(
                user_id=sample_user,
                film_id="00000000-0000-0000-0000-000000000000",
            )


def test_add_to_watchlist_duplicate_raises(app, sample_user, sample_film):
    """Adding the same film twice should not create a duplicate entry."""
    with app.app_context():
        add_to_watchlist(user_id=sample_user, film_id=sample_film)

        with pytest.raises(AlreadyInWatchlistError):
            add_to_watchlist(user_id=sample_user, film_id=sample_film)

        count = WatchlistEntry.query.filter_by(
            user_id=sample_user, film_id=sample_film
        ).count()
        assert count == 1


def test_get_watchlist_returns_newest_first(app, sample_user):
    """The watchlist should put the most recently added film first."""
    with app.app_context():
        older_film = Film(title="Zodiac", year=2007, genre="Thriller")
        newer_film = Film(title="Arrival", year=2016, genre="Sci-Fi")
        db.session.add_all([older_film, newer_film])
        db.session.commit()

        older_entry = WatchlistEntry(
            user_id=sample_user,
            film_id=older_film.id,
            date_added=datetime.now(timezone.utc) - timedelta(days=1),
        )
        newer_entry = WatchlistEntry(
            user_id=sample_user,
            film_id=newer_film.id,
            date_added=datetime.now(timezone.utc),
        )
        db.session.add_all([older_entry, newer_entry])
        db.session.commit()

        watchlist = get_watchlist(sample_user)

        assert [film["title"] for film in watchlist] == ["Arrival", "Zodiac"]
