from app.db.models import ProductFamilyModel
from app.domain.exceptions import EmptyConfigurationError, MissingRequiredAttributesError


class ConfigurationValidator:
    def validate_presence(
        self,
        family: ProductFamilyModel,
        provided_attribute_codes: set[str],
    ) -> None:
        if not provided_attribute_codes:
            raise EmptyConfigurationError(
                "Configuration must contain at least one attribute value."
            )

        required_attributes = {
            attribute.code
            for attribute in family.attributes
            if attribute.is_required
        }

        missing_attributes = sorted(required_attributes - provided_attribute_codes)
        if missing_attributes:
            raise MissingRequiredAttributesError(missing_attributes)