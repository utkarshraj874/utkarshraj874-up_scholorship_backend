ALLOWED_CATEGORIES = {
    "aadhaar_card",
    "tenth_marksheet",
    "twelfth_marksheet",
    "income_certificate",
    "category_certificate",
    "domicile_certificate",
    "bank_passbook",
    "ration_card",
    "profile_photo",
}


def validate_category(category: str):
    if category not in ALLOWED_CATEGORIES:
        raise ValueError(
            f"Invalid document category: {category}"
        )


def validate_document_details(category: str, data: dict):
    validate_category(category)

    if category == "aadhaar_card":
        if not data.get("aadhaar_number"):
            raise ValueError("Aadhaar number is required")

    elif category == "tenth_marksheet":
        required_fields = [
            "tenth_roll_number",
            "tenth_board",
            "tenth_passing_year",
            "tenth_percentage",
        ]

        check_required_fields(data, required_fields)

    elif category == "twelfth_marksheet":
        required_fields = [
            "twelfth_roll_number",
            "twelfth_board",
            "twelfth_passing_year",
            "twelfth_percentage",
        ]

        check_required_fields(data, required_fields)

    elif category == "income_certificate":
        required_fields = [
            "document_number",
            "issue_date",
            "total_income",
        ]

        check_required_fields(data, required_fields)

    elif category == "category_certificate":
        required_fields = [
            "document_number",
            "issue_date",
            "certificate_category",
        ]

        check_required_fields(data, required_fields)

    elif category == "domicile_certificate":
        required_fields = [
            "document_number",
            "issue_date",
            "domicile_state",
        ]

        check_required_fields(data, required_fields)

    elif category == "bank_passbook":
        required_fields = [
            "bank_account_number",
            "bank_ifsc",
            "bank_name",
            "bank_branch",
        ]

        check_required_fields(data, required_fields)

    elif category == "ration_card":
        if not data.get("ration_card_number"):
            raise ValueError("Ration card number is required")


def check_required_fields(data: dict, fields: list):
    for field in fields:
        value = data.get(field)

        if value is None or value == "":
            raise ValueError(f"{field} is required")