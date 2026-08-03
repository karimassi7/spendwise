from decimal import Decimal

from domain.user_profile import UserProfile
from repositories.profile_repository import ProfileRepository


class ProfileService:
    """Provide user profile operations."""

    def __init__(
        self,
        profile_repo: ProfileRepository,
        dependent_repositories: tuple[object, ...] = (),
    ) -> None:
        self.profile_repo = profile_repo
        self.dependent_repositories = dependent_repositories

    def create_profile(
        self,
        name: str,
        currency: str,
        monthly_income: Decimal,
    ) -> UserProfile:
        """Create and persist a user profile."""
        profile = UserProfile(
            name=name,
            currency=currency,
            # MySQL replaces this temporary valid ID with AUTO_INCREMENT.
            user_id=1,
            monthly_income=monthly_income,
        )

        self.profile_repo.add(profile)

        return profile

    def get_profiles(self) -> list[UserProfile]:
        """Return every user profile."""
        return self.profile_repo.get_all()

    def get_profile(self, user_id: int) -> UserProfile:
        """Return the selected user profile."""
        if user_id <= 0:
            raise ValueError("Enter a valid profile ID.")
        profile = self.profile_repo.get_by_id(user_id)
        if profile is None:
            raise ValueError("This profile doesn't exist.")
        return profile

    def update_profile(
        self,
        user_id: int,
        name: str,
        currency: str,
        monthly_income: Decimal,
    ) -> UserProfile:
        """Update and persist the user profile."""
        current_profile = self.get_profile(user_id)

        updated_profile = UserProfile(
            name=name,
            currency=currency,
            user_id=current_profile.user_id,
            monthly_income=monthly_income,
        )

        self.profile_repo.update(updated_profile)

        return updated_profile

    def remove_profile(self, user_id: int) -> None:
        """Remove a profile and all financial records it owns."""
        profile = self.get_profile(user_id)
        for repository in self.dependent_repositories:
            remove_by_profile_id = repository.remove_by_profile_id
            remove_by_profile_id(user_id)
        self.profile_repo.remove(profile)
