from .models import ElectronicSignature

def create_signature(signer, meaning, record_type, record_id, comment=''):
    """
    Create an electronic signature record.
    
    Args:
        signer: Employee object (the signer)
        meaning: String (approved, rejected, reviewed, completed, released)
        record_type: String (e.g., 'COA', 'Material')
        record_id: String (the ID of the record being signed)
        comment: Optional comment
    
    Returns:
        ElectronicSignature instance
    """
    return ElectronicSignature.objects.create(
        signer=signer,
        signer_printed_name=signer.full_name_prop,
        meaning=meaning,
        record_type=record_type,
        record_id=record_id,
        comment=comment,
    )

def verify_signature(signature_id, record_content=None):
    """
    Verify a signature's integrity.
    For future use: compare hashes.
    """
    # Placeholder – implement as needed
    return True