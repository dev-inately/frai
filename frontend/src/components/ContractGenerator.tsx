import React, { useState, useRef, useEffect } from "react";
import {
  Play,
  Square,
  Download,
  FileText,
  Building2,
  MapPin,
  Users,
} from "lucide-react";
import ContractForm from "./ContractForm";
import ContractDisplay from "./ContractDisplay";
import { ContractType, BusinessContext } from "../types";

interface ContractData {
  contractId: string;
  contractType: ContractType;
  sections: any[];
  totalSections: number;
  estimatedPages: number;
  generationTime: number;
  modelUsed: string;
  htmlContent: string;
}

const ContractGenerator: React.FC = () => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [contractData, setContractData] = useState<ContractData | null>(null);
  const [streamingContent, setStreamingContent] = useState("");
  const [error, setError] = useState<string | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const handleGenerateContract = async (formData: {
    businessContext: BusinessContext;
    contractType: ContractType;
  }) => {
    setIsGenerating(true);
    setError(null);
    setStreamingContent("");
    setContractData(null);

    // Create abort controller for cancellation
    abortControllerRef.current = new AbortController();

    try {
      const response = await fetch("/api/generate-contract", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
        signal: abortControllerRef.current.signal,
      });

      if (!response.ok) {
        const data = await response.json();
        if (data) {
          console.log("reps is ", data.detail[0]?.msg, typeof data.detail);
          throw new Error(data.detail[0]?.msg);
        }
        throw new Error(`HTTP error! status: ${response.body}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error("No response body");
      }

      const decoder = new TextDecoder();
      let content = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split("\n");

        for (const line of lines) {
          if (line.includes("[END_OF_DOC=")) {
            console.log("Data is [END]", line.split("=")[1]);
            // Generation complete, get full contract
            await getFullContract(line.split("=")[1]);
            return;
          }
          if (line.startsWith("data: ")) {
            const data = line.slice(6);

            if (data.startsWith("Error:")) {
              throw new Error(data);
            } else {
              content += data;
              setStreamingContent(content);
            }
          }
        }
      }
    } catch (err: any) {
      if (err.name === "AbortError") {
        console.log("Contract generation was cancelled");
        setError("Contract generation was cancelled");
      } else {
        setError(err.message || "Failed to generate contract");
      }
    } finally {
      setIsGenerating(false);
    }
  };

  const getFullContract = async (contract_id: string) => {
    try {
      const response = await fetch("/api/generate-contract-full", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          contract_id: contract_id,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log("HTML File", data);
      setContractData(data);
    } catch (err: any) {
      setError(err.message || "Failed to get full contract");
    }
  };

  const handleStopGeneration = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    console.log("Abort ref set to false");
    setIsGenerating(false);
  };

  const handleDownload = async () => {
    if (!contractData) return;
    console.log("Contract Data", contractData);
    try {
      const response = await fetch("/api/download-contract", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          businessContext: contractData.businessContext,
          contractType: contractData.contractType,
          customSections: [],
          language: "en",
          jurisdiction: "",
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to download contract");
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `contract_${contractData.contractType}_${contractData.contractId}.html`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err: any) {
      setError(err.message || "Failed to download contract");
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
      {/* Left Column - Form */}
      <div className="space-y-6">
        <div className="card">
          <div className="flex items-center space-x-2 mb-4">
            <FileText className="h-5 w-5 text-primary-600" />
            <h2 className="text-xl font-semibold text-gray-900">
              Generate Contract
            </h2>
          </div>

          <ContractForm
            onSubmit={handleGenerateContract}
            isGenerating={isGenerating}
            onStop={handleStopGeneration}
          />
        </div>

        {/* Features */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Features</h3>
          <div className="space-y-3">
            <div className="flex items-center space-x-3">
              <Building2 className="h-5 w-5 text-primary-600" />
              <span className="text-gray-700">AI-powered generation</span>
            </div>
            <div className="flex items-center space-x-3">
              <MapPin className="h-5 w-5 text-primary-600" />
              <span className="text-gray-700">Legal jurisdiction support</span>
            </div>
            <div className="flex items-center space-x-3">
              <Users className="h-5 w-5 text-primary-600" />
              <span className="text-gray-700">Multiple contract types</span>
            </div>
          </div>
        </div>
      </div>

      {/* Right Column - Display */}
      <div className="space-y-6">
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">
              Generated Contract
            </h2>
            {contractData && (
              <button
                onClick={handleDownload}
                className="btn-primary flex items-center space-x-2"
              >
                <Download className="h-4 w-4" />
                <span>Download HTML</span>
              </button>
            )}
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
              <p className="text-red-800">{error}</p>
            </div>
          )}

          {isGenerating && (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Generating your contract...</p>
              <p className="text-sm text-gray-500 mt-2">
                This may take a few minutes
              </p>
            </div>
          )}

          {streamingContent && !contractData && (
            <ContractDisplay
              content={streamingContent}
              isStreaming={isGenerating}
            />
          )}

          {contractData && (
            <ContractDisplay
              content={contractData.htmlContent}
              isStreaming={false}
              metadata={contractData}
            />
          )}

          {!isGenerating && !streamingContent && !contractData && (
            <div className="text-center py-12 text-gray-500">
              <FileText className="h-16 w-16 mx-auto mb-4 text-gray-300" />
              <p>Your generated contract will appear here</p>
              <p className="text-sm mt-2">
                Fill out the form and click generate to get started
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ContractGenerator;
