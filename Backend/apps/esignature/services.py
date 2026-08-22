from .models import ElectronicSignature

def create_signature(signer, meaning, record_type, record_id, comment='', record_data=None):
    return ElectronicSignature.objects.create(
        signer=signer, signer_printed_name=signer.full_name, meaning=meaning,
        record_type=record_type, record_id=str(record_id), comment=comment
    )

def verify_password(user, password):
    return user.check_password(password)    