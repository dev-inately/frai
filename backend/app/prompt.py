def basePrompt(description: str):
    return f"""
    Instructions: Generate a highly comprehensive and exhaustive Legal Terms of Service document for a company (e.g OpenAI, Zoom Inc.). The document should be structured with clear headings and subheadings, use formal legal language, and cover all essential legal and operational considerations.
    
    Guidelines:
    - Include proper section numbering and formatting.
    - Document should be at least 10 pages long.
    - Ensure the language is clear, unambiguous, and covers potential legal risks comprehensively, mirroring the depth and detail found in professional legal documents like those from Google. Avoid overly simplistic or conversational language. BE VERY PROFESSIONAL
    - Identify and explain all applicable laws and regulations, including data privacy, intellectual property, and antitrust laws.
    - The Terms of Service should ideally include, but not be limited to, the following sections and detailed clauses within each:
        Introduction & Acceptance of Terms:
            Effective date.
            Agreement to terms upon access/use.
            Capacity to contract (e.g., age requirements).
            Modifications to terms (notice, acceptance).
        Definitions:
            Key terms like "Service," "User," "Content," "Platform," "We," "You," etc.
            User Accounts & Registration:
            Account creation requirements.
            Account security (passwords, unauthorized use).
            Accuracy of information.
            Suspension or termination of accounts.
        License to Use the Service:
            Grant of limited, non-exclusive, non-transferable license.
            Restrictions on use (e.g., reverse engineering, commercial use without permission).
        User Responsibilities & Conduct:
            Acceptable Use Policy (prohibited activities: illegal content, harassment, spam, malware).
            Compliance with all applicable laws.
            Responsibility for user-generated content (accuracy, legality).
            Interaction with other users.
        Intellectual Property Rights:
            Ownership of the Service/Platform (our IP).
            Ownership of User Content (user's IP).
            License granted by user for their content (e.g., to host, display, distribute).
            Copyright infringement policy (DMCA notice and takedown procedures).
            Trademarks.
        Content Disclaimers & Limitations:
            Disclaimer regarding accuracy, completeness, or reliability of content.
            No endorsement of user-generated content.
        Privacy Policy:
            Reference to and incorporation by reference of a separate Privacy Policy.
            Brief statement on data collection and use.
        Fees, Payments, & Subscriptions (if applicable):
            Pricing, billing cycles.
            Payment methods.
            Refund policies.
            Cancellations and termination of subscriptions.
            Taxes.
        Third-Party Services & Links:
            Disclaimer of responsibility for third-party websites or services.
            User's interaction with third-party services.
        Disclaimers of Warranties:
            "AS IS" and "AS AVAILABLE" basis.
            No express or implied warranties (e.g., merchantability, fitness for a particular purpose, non-infringement).
            No warranty that the service will be uninterrupted, error-free, or secure.
        Limitation of Liability:
            Exclusion of indirect, incidental, special, consequential, or punitive damages.
            Cap on total liability (e.g., amount paid by user or a fixed sum).
            Applicability to all theories of liability (contract, tort, negligence).
        Indemnification:
            User agrees to indemnify and hold harmless the service provider from claims arising from their use or breach of terms.
        Termination:
            Right to terminate or suspend user access for breach of terms.
            User's right to terminate their account.
            Survival of certain clauses post-termination.
        Governing Law & Jurisdiction:
            Specify the applicable law (e.g., State of California, USA).
            Specify the exclusive jurisdiction for disputes.
        Dispute Resolution:
            Mandatory arbitration clause (if desired), including rules and location.
            Class action waiver.
            Informal dispute resolution first.
        General Provisions:
            Entire Agreement.
            Severability.
            Waiver.
            Assignment.
            Force Majeure.
            Headings for convenience only.
    - IMPORTANT!: Any section not relevant to the customer's request can be omitted as long as it's not a legal requirement but make sure to add any field that might be missing but important to this request.
    - IMPORTANT!: When a company's location, jurisdiction or industry is specified in the user request, make sure to include the relevant laws and regulations in the document.
    
    Output Format:
    - IMPORTANT!: Ensure the document generated is structured in HTML format that is correct and can be displayed in a browser.
    - Use proper HTML tags (<h1>, <h2>, <h3>, <p>, <ul>, <li>)
    - Include CSS classes for styling
    - Structure with clear sections and subsections
    - Ensure readability and clarity
    - DO NOT start with ```html.
    
    User request: {description}
    """