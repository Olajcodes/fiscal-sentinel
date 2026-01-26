from opik.evaluation.metrics import BaseMetric, score_result

class LegalCitationMetric(BaseMetric):
    """
    A custom metric that checks if the agent cited a legal source.
    """
    def __init__(self, name="Legal_Compliance_Score"):
        super().__init__(name=name)

    # This satisfies any abstract class requirement because it accepts EVERYTHING.
    def score(self, **kwargs):
        
        # Extract 'output' safely from the arguments
        # Opik might pass it as 'output', 'model_output', or 'response'
        output = kwargs.get("output") or kwargs.get("model_output") or kwargs.get("response")
        
        # Safety Check: If we can't find the output, return 0
        if not output or not isinstance(output, str):
            return score_result.ScoreResult(
                name=self.name,
                value=0.0,
                reason="Agent returned no output"
            )

        # Define Keywords
        keywords = [
            "FTC", "Federal Trade Commission", 
            "Section", "Regulation", "Act", 
            "Clause", "Agreement", "Code", "Consumer",
            "Right", "Law"
        ]
        
        # Calculate Score
        value = 0.0
        reason = "No legal citations found."
        
        for word in keywords:
            if word.lower() in output.lower():
                value = 1.0
                reason = f"Successfully cited key term: '{word}'"
                break
        
        # Return the Result
        return score_result.ScoreResult(
            name=self.name,
            value=value,
            reason=reason
        )