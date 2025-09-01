export enum ContractType {
  TERMS_OF_SERVICE = "terms_of_service",
  PRIVACY_POLICY = "privacy_policy",
  SERVICE_AGREEMENT = "service_agreement",
  NDA = "nda",
  EMPLOYMENT_CONTRACT = "employment_contract",
  PARTNERSHIP_AGREEMENT = "partnership_agreement",
}

export interface BusinessContext {
  description: string;
  industry?: string;
  location?: string;
  company_size?: string;
}

export interface ContractGenerationRequest {
  business_context: BusinessContext;
  contract_type: ContractType;
  custom_sections?: string[];
  language: string;
  jurisdiction?: string;
}

export interface ContractSection {
  title: string;
  content: string;
  section_number: number;
  subsection_number?: number;
}

export interface ContractGenerationResponse {
  contract_id: string;
  contract_type: ContractType;
  sections: ContractSection[];
  total_sections: number;
  estimated_pages: number;
  generation_time: number;
  model_used: string;
}
