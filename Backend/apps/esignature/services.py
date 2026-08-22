import hashlib
import json
from django.utils import timezone
from .models import ElectronicSignature


def create_signature(
    signer,
    meaning,
    record_type,
    record_id,
    comment='',
    record_data=None
):
    """
    Create an electronic signature record.
    
    Args:
        signer: Employee object (the signer)
        meaning: String (approved, rejected, reviewed, completed, released, verified)
        record_type: String (e.g., 'COA', 'Material')
        record_id: String (the ID of the record being signed)
        comment: Optional comment
        record_data: Optional dict of record data for hash computation
    
    Returns:
        ElectronicSignature instance
    """
    # Compute record hash if data provided
    record_hash = ''
    if record_data:
        record_str = json.dumps(record_data, sort_keys=True, default=str)
        record_hash = hashlib.sha256(record_str.encode()).hexdigest()
    
    # Compute signature hash
    sig_data = f"{signer.id}:{meaning}:{record_type}:{record_id}:{timezone.now().isoformat()}"
    signature_hash = hashlib.sha256(sig_data.encode()).hexdigest()
    
    return ElectronicSignature.objects.create(
        signer=signer,
        signer_printed_name=signer.full_name,
        signer_email=signer.email,
        meaning=meaning,
        record_type=record_type,
        record_id=str(record_id),
        comment=comment,
        record_hash=record_hash,
        signature_hash=signature_hash,
        is_verified=True,
        verification_date=timezone.now()
    )


def verify_signature(signature_id, record_content=None):
    """
    Verify a signature's integrity.
    
    Args:
        signature_id: UUID of the signature to verify
        record_content: Optional current record content for hash comparison
    
    Returns:
        Tuple (is_valid: bool, message: str)
    """
    try:
        signature = ElectronicSignature.objects.get(id=signature_id)
    except ElectronicSignature.DoesNotExist:
        return False, "Signature not found"
    
    if not signature.is_verified:
        return False, "Signature was not verified"
    
    # Verify hash if record content provided
    if record_content and signature.record_hash:
        record_str = json.dumps(record_content, sort_keys=True, default=str)
        computed_hash = hashlib.sha256(record_str.encode()).hexdigest()
        if computed_hash != signature.record_hash:
            return False, "Record content has been modified since signing"
    
    return True, "Signature is valid"


def verify_password(user, password):
    """
    Verify user password for e-signature.
    
    Args:
        user: Employee object
        password: Password to verify
    
    Returns:
        bool: True if password is correct
    """
    return user.check_password(password)