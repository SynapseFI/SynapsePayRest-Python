from .base_node import BaseNode


class WireIntNode(BaseNode):
    """Represents a WIRE-INT node
    """

    @classmethod
    def payload_for_create(cls, nickname, bank_name, account_number, swift,
                           name_on_account, address, **kwargs):
        payload = super().payload_for_create('WIRE-INT',
                                             nickname=nickname,
                                             bank_name=bank_name,
                                             account_number=account_number,
                                             name_on_account=name_on_account,
                                             address=address,
                                             swift=swift,
                                             **kwargs)
        # payload['info']['swift'] = swift
        return payload
