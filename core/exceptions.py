"""Custom exceptions for the application."""


class FreelancehuntAutomizerError(Exception):
    """Base exception for all application errors."""
    pass


# Scraping exceptions
class ScrapingError(FreelancehuntAutomizerError):
    """Base exception for scraping errors."""
    pass


class ElementNotFoundError(ScrapingError):
    """Raised when a required element is not found on the page."""
    pass


class PageLoadError(ScrapingError):
    """Raised when a page fails to load."""
    pass


class ParsingError(ScrapingError):
    """Raised when parsing data from page fails."""
    pass


# Authentication exceptions
class AuthenticationError(FreelancehuntAutomizerError):
    """Base exception for authentication errors."""
    pass


class LoginFailedError(AuthenticationError):
    """Raised when login fails."""
    pass


class MFARequiredError(AuthenticationError):
    """Raised when MFA is required but not provided."""
    pass


class InvalidCredentialsError(AuthenticationError):
    """Raised when credentials are invalid."""
    pass


# Database exceptions
class DatabaseError(FreelancehuntAutomizerError):
    """Base exception for database errors."""
    pass


class ProjectNotFoundError(DatabaseError):
    """Raised when a project is not found in database."""
    pass


class DuplicateProjectError(DatabaseError):
    """Raised when trying to create a duplicate project."""
    pass


# AI exceptions
class AIError(FreelancehuntAutomizerError):
    """Base exception for AI-related errors."""
    pass


class AIResponseError(AIError):
    """Raised when AI returns invalid or empty response."""
    pass


class AITimeoutError(AIError):
    """Raised when AI request times out."""
    pass


# Bidding exceptions
class BiddingError(FreelancehuntAutomizerError):
    """Base exception for bidding errors."""
    pass


class BidAlreadyPlacedError(BiddingError):
    """Raised when bid is already placed on a project."""
    pass


class NoMoreBidsError(BiddingError):
    """Raised when no more bids are allowed."""
    pass


class TooManyBidsError(BiddingError):
    """Raised when too many bids have been placed."""
    pass


class BidSubmissionError(BiddingError):
    """Raised when bid submission fails."""
    pass

