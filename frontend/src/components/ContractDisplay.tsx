import React from "react";
import { FileText, Clock, Hash, User } from "lucide-react";

interface ContractDisplayProps {
  content: string;
  isStreaming: boolean;
  metadata?: any;
}

const ContractDisplay: React.FC<ContractDisplayProps> = ({
  content,
  isStreaming,
  metadata,
}) => {
  const formatContractType = (type: string) => {
    return type.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase());
  };

  return (
    <div className="space-y-4">
      {/* Metadata */}
      {metadata && (
        <div className="bg-gray-50 rounded-lg p-4 space-y-3">
          <h3 className="font-medium text-gray-900">Contract Details</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div className="flex items-center space-x-2">
              <FileText className="h-4 w-4 text-gray-500" />
              <span className="text-gray-600">
                {formatContractType(metadata.contract_type)}
              </span>
            </div>
            <div className="flex items-center space-x-2">
              <Hash className="h-4 w-4 text-gray-500" />
              <span className="text-gray-600">
                {metadata.total_sections} sections
              </span>
            </div>
            <div className="flex items-center space-x-2">
              <FileText className="h-4 w-4 text-gray-500" />
              <span className="text-gray-600">
                ~{metadata.estimated_pages} pages
              </span>
            </div>
            <div className="flex items-center space-x-2">
              <Clock className="h-4 w-4 text-gray-500" />
              <span className="text-gray-600">{metadata.generation_time}s</span>
            </div>
          </div>
          <div className="text-xs text-gray-500">
            Generated using {metadata.model_used}
          </div>
        </div>
      )}

      {/* Contract Content */}
      <div className="border border-gray-200 rounded-lg overflow-hidden">
        <div className="bg-gray-50 px-4 py-3 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h3 className="font-medium text-gray-900">Generated Contract</h3>
            {isStreaming && (
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-sm text-gray-600">Live generation</span>
              </div>
            )}
          </div>
        </div>

        <div className="max-h-96 overflow-y-auto">
          <div
            className="p-4 prose prose-sm max-w-none"
            dangerouslySetInnerHTML={{ __html: content }}
          />
        </div>
      </div>

      {/* Streaming Indicator */}
      {isStreaming && (
        <div className="text-center py-4">
          <div className="flex items-center justify-center space-x-2 text-sm text-gray-600">
            <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
            <span>Generating contract content...</span>
          </div>
        </div>
      )}

      {/* Content Stats */}
      {content && (
        <div className="text-xs text-gray-500 text-center">
          <p>
            Content length: {content.length} characters
            {content.includes("<") && ` • HTML formatted`}
          </p>
        </div>
      )}
    </div>
  );
};

export default ContractDisplay;
