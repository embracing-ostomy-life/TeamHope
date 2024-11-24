from django.conf import settings
from .docusign_token_manager import DocuSignTokenManager
from docusign_esign import EnvelopesApi, EnvelopeDefinition, TemplateRole, AccountsApi


class DocuSignEmailSender:
    def __init__(self):
        self.token_manager = DocuSignTokenManager()
        self.api_client = self.token_manager.get_api_client()
        self.account_id = settings.DS_ACCOUNT_ID

    def send_email(
        self,
        customer_email,
        customer_name,
        template_id=settings.DS_ALIVE_KICKING_TEMPLATE_ID,
    ):
        """Send an email to the customer to sign a document using a template."""
        try:
            # Initialize the DocuSign Envelopes API
            envelopes_api = EnvelopesApi(self.api_client)
            # Define the role for the template
            template_role = TemplateRole(
                email=customer_email,
                name=customer_name,
                role_name="signer",  # Must match the role name defined in the template
            )

            # Create an envelope definition
            envelope_definition = EnvelopeDefinition(
                template_id=template_id,
                status="sent",  # "sent" to email immediately; "created" to save as draft
            )
            envelope_definition.template_roles = [template_role]
            # Send the envelope
            envelope = envelopes_api.create_envelope(
                account_id=self.account_id, envelope_definition=envelope_definition
            )

            return {"envelope_id": envelope.envelope_id, "status": "Email sent"}
        except Exception as e:
            raise Exception(f"Failed to send DocuSign email: {str(e)}")
