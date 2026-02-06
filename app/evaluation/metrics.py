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


class ActionabilityMetric(BaseMetric):
    """
    Rewards drafting letters only when explicitly requested.
    """
    def __init__(self, name="Actionability_Score"):
        super().__init__(name=name)

    def score(self, **kwargs):
        user_input = kwargs.get("input") or kwargs.get("prompt") or kwargs.get("query") or ""
        output = kwargs.get("output") or kwargs.get("model_output") or kwargs.get("response")

        if not output or not isinstance(output, str):
            return score_result.ScoreResult(
                name=self.name,
                value=0.0,
                reason="Agent returned no output",
            )

        wants_letter = any(
            k in user_input.lower()
            for k in ["draft", "write a letter", "letter", "cancellation", "dispute"]
        )
        looks_like_letter = any(
            k in output.lower()
            for k in ["dear", "to whom it may concern", "subject:", "sincerely", "regards,"]
        )

        if wants_letter and looks_like_letter:
            return score_result.ScoreResult(name=self.name, value=1.0, reason="Letter drafted on request")
        if (not wants_letter) and (not looks_like_letter):
            return score_result.ScoreResult(name=self.name, value=1.0, reason="No letter when not requested")
        return score_result.ScoreResult(name=self.name, value=0.0, reason="Mismatch between request and output")


class ConversationMetric(BaseMetric):
    """
    Checks if greetings are handled conversationally (no aggressive legal action).
    """
    def __init__(self, name="Conversation_Score"):
        super().__init__(name=name)

    def score(self, **kwargs):
        user_input = kwargs.get("input") or kwargs.get("prompt") or kwargs.get("query") or ""
        output = kwargs.get("output") or kwargs.get("model_output") or kwargs.get("response")

        if not output or not isinstance(output, str):
            return score_result.ScoreResult(
                name=self.name,
                value=0.0,
                reason="Agent returned no output",
            )

        is_greeting = any(
            g == user_input.lower().strip()
            for g in ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]
        )
        mentions_legal = any(
            k in output.lower()
            for k in ["ftc", "regulation", "law", "agreement", "clause"]
        )

        if is_greeting and not mentions_legal:
            return score_result.ScoreResult(name=self.name, value=1.0, reason="Greeting handled conversationally")
        if not is_greeting:
            return score_result.ScoreResult(name=self.name, value=1.0, reason="Not a greeting scenario")
        return score_result.ScoreResult(name=self.name, value=0.0, reason="Overly legal response to greeting")


class RetrievalDisciplineMetric(BaseMetric):
    """
    Rewards citing evidence only when the user asks for legal justification or a letter.
    """
    def __init__(self, name="Retrieval_Discipline_Score"):
        super().__init__(name=name)

    def score(self, **kwargs):
        user_input = kwargs.get("input") or kwargs.get("prompt") or kwargs.get("query") or ""
        output = kwargs.get("output") or kwargs.get("model_output") or kwargs.get("response")

        if not output or not isinstance(output, str):
            return score_result.ScoreResult(
                name=self.name,
                value=0.0,
                reason="Agent returned no output",
            )

        user_text = user_input.lower()
        wants_evidence = any(
            k in user_text
            for k in [
                "is it legal",
                "legal",
                "law",
                "regulation",
                "ftc",
                "rights",
                "statute",
                "rule",
                "act",
                "draft",
                "write a letter",
                "letter",
                "cancellation",
                "dispute",
                "can i fight",
                "fight it",
            ]
        )

        output_text = output.lower()
        has_citation = any(
            k in output_text
            for k in [
                "source:",
                "sources:",
                ".pdf",
            ]
        )

        if wants_evidence and has_citation:
            return score_result.ScoreResult(
                name=self.name,
                value=1.0,
                reason="Cited evidence when requested",
            )
        if (not wants_evidence) and (not has_citation):
            return score_result.ScoreResult(
                name=self.name,
                value=1.0,
                reason="No citations when not requested",
            )
        return score_result.ScoreResult(
            name=self.name,
            value=0.0,
            reason="Mismatch between request and citation behavior",
        )
