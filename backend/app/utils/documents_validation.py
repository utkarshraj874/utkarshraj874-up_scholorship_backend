ALLOWED_CATEGORIES = {
    "aadhaar_card",
    "tenth_marksheet",
    "twelfth_marksheet",
    "income_certificate",
    "category_certificate",
    "domicile_certificate",
    "bank_passbook",
    "gap_certificate",
    "last_semester_result",
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
        ]

        check_required_fields(data, required_fields)
        validate_education_score(data, "tenth")

    elif category == "twelfth_marksheet":
        required_fields = [
            "twelfth_roll_number",
            "twelfth_board",
            "twelfth_passing_year",
        ]

        check_required_fields(data, required_fields)
        validate_education_score(data, "twelfth")

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

def check_required_fields(data: dict, fields: list):
    for field in fields:
        value = data.get(field)

        if value is None or value == "":
            raise ValueError(f"{field} is required")


def validate_education_score(data: dict, prefix: str):
    percentage = data.get(f"{prefix}_percentage")
    cgpa = data.get(f"{prefix}_cgpa")
    board = (data.get(f"{prefix}_board") or "").strip().upper()
    has_percentage = percentage is not None and percentage != ""
    has_cgpa = cgpa is not None and cgpa != ""

    if board == "CBSE":
        if has_percentage == has_cgpa:
            raise ValueError(f"Provide either {prefix} percentage or CGPA for CBSE")
    else:
        if not has_percentage:
            raise ValueError(f"{prefix} percentage is required for this board")
        if has_cgpa:
            raise ValueError("CGPA entry is available only for CBSE")
