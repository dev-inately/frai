import React, { useState } from "react";
import { Play, Square } from "lucide-react";
import { ContractType, BusinessContext } from "../types";

interface ContractFormProps {
  onSubmit: (formData: {
    businessContext: BusinessContext;
    contractType: ContractType;
    customSections: string[];
    language: string;
    jurisdiction: string;
  }) => void;
  isGenerating: boolean;
  onStop: () => void;
}

const ContractForm: React.FC<ContractFormProps> = ({
  onSubmit,
  isGenerating,
  onStop,
}) => {
  const [businessDescription, setBusinessDescription] = useState("");
  const [contractType, setContractType] = useState<ContractType>(
    ContractType.TERMS_OF_SERVICE
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!businessDescription.trim()) {
      alert("Please provide a business description");
      return;
    }

    const formData = {
      business_context: {
        description: businessDescription.trim(),
      },
      contract_type: contractType,
    };

    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Business Description */}
      <div>
        <label
          htmlFor="businessDescription"
          className="block text-sm font-medium text-gray-700 mb-2"
        >
          Business Description *
        </label>
        <textarea
          id="businessDescription"
          value={businessDescription}
          onChange={(e) => setBusinessDescription(e.target.value)}
          placeholder="Describe your business, what you do, your target market, and any specific requirements..."
          className="input-field h-32 resize-none"
          required
        />
        <p className="text-sm text-gray-500 mt-1">
          Be specific about your business model, industry, and any unique
          aspects
        </p>
      </div>

      {/* Business Details */}
      {/* <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label
            htmlFor="industry"
            className="block text-sm font-medium text-gray-700 mb-2"
          >
            Industry
          </label>
          <input
            type="text"
            id="industry"
            value={industry}
            onChange={(e) => setIndustry(e.target.value)}
            placeholder="e.g., SaaS, Healthcare, E-commerce"
            className="input-field"
          />
        </div>

        <div>
          <label
            htmlFor="location"
            className="block text-sm font-medium text-gray-700 mb-2"
          >
            Location
          </label>
          <input
            type="text"
            id="location"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            placeholder="e.g., New York, California, EU"
            className="input-field"
          />
        </div>

        <div>
          <label
            htmlFor="companySize"
            className="block text-sm font-medium text-gray-700 mb-2"
          >
            Company Size
          </label>
          <select
            id="companySize"
            value={companySize}
            onChange={(e) => setCompanySize(e.target.value)}
            className="input-field"
          >
            <option value="">Select size</option>
            <option value="Startup">Startup (1-10 employees)</option>
            <option value="SME">SME (11-250 employees)</option>
            <option value="Enterprise">Enterprise (250+ employees)</option>
          </select>
        </div>
      </div> */}

      {/* Contract Type */}
      {/* <div>
        <label
          htmlFor="contractType"
          className="block text-sm font-medium text-gray-700 mb-2"
        >
          Contract Type *
        </label>
        <select
          id="contractType"
          value={contractType}
          onChange={(e) => setContractType(e.target.value as ContractType)}
          className="input-field"
          required
        >
          {contractTypes.map((type) => (
            <option key={type.value} value={type.value}>
              {type.label}
            </option>
          ))}
        </select>
        {contractTypes.find((t) => t.value === contractType)?.description && (
          <p className="text-sm text-gray-500 mt-1">
            {contractTypes.find((t) => t.value === contractType)?.description}
          </p>
        )}
      </div> */}

      {/* Submit Button */}
      <div className="pt-4">
        {!isGenerating ? (
          <button
            type="submit"
            className="btn-primary w-full flex items-center justify-center space-x-2 py-3"
            disabled={!businessDescription.trim()}
          >
            <Play className="h-5 w-5" />
            <span>Generate Contract</span>
          </button>
        ) : (
          <button
            type="button"
            onClick={(e) => {
              e.preventDefault();
              onStop();
            }}
            className="btn-secondary w-full flex items-center justify-center space-x-2 py-3"
          >
            <Square className="h-5 w-5" />
            <span>Stop Generation</span>
          </button>
        )}
      </div>

      {/* Help Text */}
      <div className="text-sm text-gray-500 text-center">
        <p>
          Generation typically takes 2-5 minutes depending on contract
          complexity
        </p>
        <p className="mt-1">You can stop generation at any time</p>
      </div>
    </form>
  );
};

export default ContractForm;
