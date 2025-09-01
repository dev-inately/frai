import React from "react";

const Footer: React.FC = () => {
  return (
    <footer className="bg-gray-800 text-white py-8 mt-16">
      <div className="container mx-auto px-4">
        <div className="text-center">
          <p className="text-gray-300 mb-4">
            AI Contract Generator - Professional legal documents powered by
            artificial intelligence
          </p>
          <div className="text-sm text-gray-400">
            <p className="mb-2">
              ⚠️ Disclaimer: This tool generates AI-assisted legal documents.
              Please review with qualified legal counsel before use.
            </p>
            <p>© 2024 FirstReadAI. All rights reserved.</p>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
