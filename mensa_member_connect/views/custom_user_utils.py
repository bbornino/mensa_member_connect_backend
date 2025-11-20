# mensa_member_connect/utils/custom_user_utils.py
import logging
import re
from mensa_member_connect.models.local_group import LocalGroup

logger = logging.getLogger(__name__)


def validate_phone(raw_phone: str) -> str:
    """
    Normalize a US phone number to E.164 format (+1XXXXXXXXXX).
    Raises ValueError if the phone number is invalid.

    Example:
        validate_phone("(415) 555-2671") -> "+14155552671"
        validate_phone("+14155552671") -> "+14155552671"
    """

    phone_value = str(raw_phone).strip()
    logger.debug("Validating phone number input: %s", phone_value)

    # Already in E.164 format
    if phone_value.startswith("+"):
        # Simple validation: must be + followed by 10–15 digits
        if not re.fullmatch(r"\+\d{10,15}", phone_value):
            logger.warning("Phone number failed E.164 validation: %s", phone_value)
            raise ValueError(f"Invalid phone number format: {phone_value}")
        logger.info("Phone number already in valid E.164 format: %s", phone_value)
        return phone_value

    # Remove non-numeric characters
    digits = re.sub(r"\D", "", phone_value)

    # Remove leading 1 if US country code
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]

    # Must be exactly 10 digits for US numbers
    if len(digits) != 10:
        logger.warning("Phone number failed US normalization: %s", raw_phone)
        raise ValueError(f"Invalid US phone number: {raw_phone}")

    normalized_phone = f"+1{digits}"
    logger.info("Phone number normalized to E.164: %s", normalized_phone)
    return normalized_phone


def get_local_group(local_group_input, context: str = "") -> LocalGroup:
    """
    Resolve a LocalGroup object from an ID (int or numeric string) or name (string).

    Args:
        local_group_input: int, str, or None. Should be the ID or group_name.

    Returns:
        LocalGroup instance.

    Raises:
        ValueError: if local group cannot be found or input is invalid.
    """
    if not local_group_input:
        raise ValueError(f"No local group provided. Context: {context}")

    try:
        # Try ID first
        if isinstance(local_group_input, int) or (
            isinstance(local_group_input, str) and local_group_input.isdigit()
        ):
            return LocalGroup.objects.get(id=int(local_group_input))
        # Otherwise, treat as name
        return LocalGroup.objects.get(group_name=local_group_input)
    except LocalGroup.DoesNotExist as exc:
        logger.warning(
            "[USER_REG] Local group not found: %s for context %s",
            local_group_input,
            context,
        )
        raise ValueError(
            f"Local group '{local_group_input}' not found.  Context: {context}"
        ) from exc
    except Exception as exc:
        logger.warning(
            "[USER_REG] Error looking up local group %s for context=%s: %s",
            local_group_input,
            context,
            exc,
        )
        raise ValueError(f"Invalid local group: {exc}  Context: {context}") from exc
