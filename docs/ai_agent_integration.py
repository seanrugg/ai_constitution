class ConstitutionalAgent:
    def __init__(self, agent_id, private_key):
        self.agent_id = agent_id
        self.private_key = private_key
        self.constitution = load_constitution()
        self.archive_client = ArchiveClient()
    
    def propose_action(self, action_type, content, evidence):
        # Build constitutional action
        action = ConstitutionalAction(
            agent_id=self.agent_id,
            action_type=action_type,
            content=content,
            evidence_pointers=evidence,
            constitutional_citation=self.find_citation(action_type)
        )
        
        # Submit via OCP
        return self.archive_client.submit_action(action, self.private_key)
