import re
from typing import Tuple, List, Dict

# Regex patterns for PII
EMAIL_REGEX = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b')
PHONE_REGEX = re.compile(r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b')
CARD_REGEX = re.compile(r'\b(?:\d[ -]*?){13,16}\b')
PAN_REGEX = re.compile(r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b')
AADHAAR_REGEX = re.compile(r'\b[2-9]{1}[0-9]{3}[ -]?[0-9]{4}[ -]?[0-9]{4}\b')

def luhn_check(card_number: str) -> bool:
    digits = [int(d) for d in re.sub(r'\D', '', card_number)]
    if len(digits) < 13 or len(digits) > 19:
        return False
    checksum = 0
    reverse_digits = digits[::-1]
    for i, d in enumerate(reverse_digits):
        if i % 2 == 1:
            doubled = d * 2
            checksum += doubled - 9 if doubled > 9 else doubled
        else:
            checksum += d
    return checksum % 10 == 0

class PIIMasker:
    def mask(self, text: str) -> Tuple[str, List[str]]:
        """
        Masks detected PII in text and returns the masked text and list of masked types.
        """
        masked_types: List[str] = []
        result = text

        # 1. Mask Email
        emails = EMAIL_REGEX.findall(result)
        if emails:
            masked_types.append("email")
            for i, email in enumerate(emails, 1):
                result = result.replace(email, f"<EMAIL_{i}>")

        # 2. Mask Credit/Debit Card with Luhn Verification
        cards = CARD_REGEX.findall(result)
        card_count = 0
        for card in cards:
            clean_card = re.sub(r'\D', '', card)
            if len(clean_card) >= 13 and luhn_check(clean_card):
                card_count += 1
                result = result.replace(card, f"<CARD_{card_count}>")
        if card_count > 0:
            masked_types.append("credit_card")

        # 3. Mask Aadhaar / PAN
        pan_matches = PAN_REGEX.findall(result)
        if pan_matches:
            masked_types.append("national_id_pan")
            for i, pan in enumerate(pan_matches, 1):
                result = result.replace(pan, f"<PAN_ID_{i}>")

        aadhaar_matches = AADHAAR_REGEX.findall(result)
        if aadhaar_matches:
            masked_types.append("national_id_aadhaar")
            for i, aadh in enumerate(aadhaar_matches, 1):
                result = result.replace(aadh, f"<AADHAAR_ID_{i}>")

        # 4. Mask Phone numbers
        phones = PHONE_REGEX.findall(result)
        if phones:
            masked_types.append("phone_number")
            for i, phone in enumerate(phones, 1):
                result = result.replace(phone, f"<PHONE_{i}>")

        return result, list(set(masked_types))

pii_masker = PIIMasker()
