import React from "react";
import { FileText, Github } from "lucide-react";

const Header: React.FC = () => {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <FileText className="h-8 w-8 text-primary-600" />
            <h1 className="text-2xl font-bold text-gray-900">FirstReadAI</h1>
          </div>

          <nav className="flex items-center space-x-6">
            <a
              href="#features"
              className="text-gray-600 hover:text-gray-900 transition-colors duration-200"
            >
              Features
            </a>
            <a
              href="#about"
              className="text-gray-600 hover:text-gray-900 transition-colors duration-200"
            >
              About
            </a>
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition-colors duration-200"
            >
              <Github className="h-5 w-5" />
              <span>GitHub</span>
            </a>
          </nav>
        </div>
      </div>
    </header>
  );
};

export default Header;
