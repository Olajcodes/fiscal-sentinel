'use client';

import React, { useState, useCallback } from 'react';
import { X, Upload, FileText, CheckCircle, AlertCircle } from 'lucide-react';
import { api } from '@/lib/api';

interface UploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

const UploadModal: React.FC<UploadModalProps> = ({ isOpen, onClose, onSuccess }) => {
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [step, setStep] = useState<'upload' | 'preview' | 'confirm' | 'success'>('upload');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [previewData, setPreviewData] = useState<any>(null);
  const [mapping, setMapping] = useState<Record<string, string>>({});

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    const files = e.dataTransfer.files;
    if (files && files[0]) {
      handleFile(files[0]);
    }
  }, []);

  const handleFile = (selectedFile: File) => {
    const validTypes = [
      'text/csv',
      'application/vnd.ms-excel',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'application/pdf',
      'application/json',
    ];
    
    if (!validTypes.includes(selectedFile.type) && !selectedFile.name.match(/\.(csv|xlsx|xls|pdf|json)$/)) {
      setError('Please upload a CSV, Excel, PDF, or JSON file');
      return;
    }
    
    if (selectedFile.size > 10 * 1024 * 1024) { // 10MB limit
      setError('File size must be less than 10MB');
      return;
    }
    
    setFile(selectedFile);
    setError(null);
  };

  const handlePreview = async () => {
    if (!file) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const data = await api.previewTransactions(file);
      setPreviewData(data);
      setMapping(data.suggested_mapping);
      setStep('preview');
    } catch (err: any) {
      setError(err.message || 'Failed to preview file');
    } finally {
      setIsLoading(false);
    }
  };

  const handleConfirm = async () => {
    if (!previewData) return;
    
    setIsLoading(true);
    
    try {
      await api.confirmTransactions(previewData.preview_id, mapping);
      setStep('success');
      setTimeout(() => {
        onSuccess();
        onClose();
        resetModal();
      }, 2000);
    } catch (err: any) {
      setError(err.message || 'Failed to confirm upload');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDirectUpload = async () => {
    if (!file) return;
    
    setIsLoading(true);
    
    try {
      await api.uploadTransactions(file);
      setStep('success');
      setTimeout(() => {
        onSuccess();
        onClose();
        resetModal();
      }, 2000);
    } catch (err: any) {
      setError(err.message || 'Failed to upload file');
    } finally {
      setIsLoading(false);
    }
  };

  const resetModal = () => {
    setFile(null);
    setStep('upload');
    setError(null);
    setPreviewData(null);
    setMapping({});
    setIsLoading(false);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-full items-center justify-center p-4">
        {/* Backdrop */}
        <div 
          className="fixed inset-0 bg-black/50 transition-opacity"
          onClick={onClose}
        />

        {/* Modal */}
        <div className="relative w-full max-w-2xl rounded-2xl bg-white shadow-2xl">
          {/* Header */}
          <div className="flex items-center justify-between border-b border-gray-200 p-4 md:p-6">
            <div>
              <h2 className="text-lg md:text-xl font-bold text-gray-900">
                {step === 'upload' && 'Upload Transactions'}
                {step === 'preview' && 'Preview & Map Columns'}
                {step === 'confirm' && 'Confirm Upload'}
                {step === 'success' && 'Upload Successful'}
              </h2>
              <p className="text-xs md:text-sm text-gray-600">
                {step === 'upload' && 'Upload your bank statements or transaction files'}
                {step === 'preview' && 'Map columns to transaction fields'}
                {step === 'confirm' && 'Review and confirm your upload'}
                {step === 'success' && 'Transactions have been successfully imported'}
              </p>
            </div>
            <button
              onClick={onClose}
              className="rounded-lg p-1.5 md:p-2 hover:bg-gray-100 transition-colors"
            >
              <X className="h-5 w-5 text-gray-500" />
            </button>
          </div>

          {/* Body */}
          <div className="p-4 md:p-6">
            {error && (
              <div className="mb-4 md:mb-6 flex items-center gap-2 md:gap-3 rounded-lg border border-red-200 bg-red-50 p-3 md:p-4">
                <AlertCircle className="h-4 w-4 md:h-5 md:w-5 text-red-600 flex-shrink-0" />
                <span className="text-xs md:text-sm font-medium text-red-700">{error}</span>
              </div>
            )}

            {step === 'upload' && (
              <div>
                <div
                  className={`border-2 border-dashed rounded-xl p-6 md:p-8 lg:p-12 text-center transition-colors ${
                    dragActive 
                      ? 'border-blue-500 bg-blue-50' 
                      : 'border-gray-300 hover:border-gray-400'
                  }`}
                  onDragEnter={handleDrag}
                  onDragLeave={handleDrag}
                  onDragOver={handleDrag}
                  onDrop={handleDrop}
                >
                  <div className="mx-auto mb-3 md:mb-4 flex h-12 w-12 md:h-16 md:w-16 items-center justify-center rounded-full bg-blue-100">
                    <Upload className="h-6 w-6 md:h-8 md:w-8 text-blue-600" />
                  </div>
                  
                  {file ? (
                    <div className="space-y-3 md:space-y-4">
                      <div className="flex items-center justify-center gap-2 md:gap-3">
                        <FileText className="h-5 w-5 md:h-6 md:w-6 text-gray-400" />
                        <div className="text-left">
                          <p className="font-medium text-gray-900 text-sm md:text-base">{file.name}</p>
                          <p className="text-xs md:text-sm text-gray-500">
                            {(file.size / 1024).toFixed(1)} KB
                          </p>
                        </div>
                      </div>
                      <button
                        onClick={() => setFile(null)}
                        className="text-xs md:text-sm text-red-600 hover:text-red-700"
                      >
                        Remove file
                      </button>
                    </div>
                  ) : (
                    <div>
                      <p className="mb-1 md:mb-2 text-base md:text-lg font-medium text-gray-900">
                        Drop your file here
                      </p>
                      <p className="mb-4 md:mb-6 text-sm text-gray-600">
                        or click to browse (CSV, Excel, PDF, JSON)
                      </p>
                      <input
                        type="file"
                        id="file-upload"
                        className="hidden"
                        onChange={(e) => e.target.files && handleFile(e.target.files[0])}
                      />
                      <label
                        htmlFor="file-upload"
                        className="btn-primary cursor-pointer inline-block  bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-2 rounded-lg font-medium hover:from-blue-700 hover:to-purple-700 transition-all duration-200 shadow-sm hover:shadow disabled:opacity-50 disabled:cursor-not-allowed;"
                      >
                        Browse Files
                      </label>
                    </div>
                  )}
                </div>

                <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="rounded-lg border border-gray-200 p-4">
                    <h4 className="font-medium text-gray-900 mb-2 text-sm md:text-base">Direct Upload</h4>
                    <p className="text-xs md:text-sm text-gray-600 mb-3 md:mb-4">
                      Upload and process immediately with auto-detection
                    </p>
                    <button
                      onClick={handleDirectUpload}
                      disabled={!file || isLoading}
                      className="btn-secondary w-full text-sm bg-gray-100 text-gray-700 px-4 py-2 rounded-lg font-medium hover:bg-gray-200 transition-all duration-200 border border-gray-300 disabled:opacity-50 disabled:cursor-not-allowed;"
                    >
                      {isLoading ? 'Uploading...' : 'Upload Now'}
                    </button>
                  </div>
                  
                  <div className="rounded-lg border border-gray-200 bg-gray-50 p-4">
                    <h4 className="font-medium text-gray-900 mb-2 text-sm md:text-base">Preview First</h4>
                    <p className="text-xs md:text-sm text-gray-600 mb-3 md:mb-4">
                      Preview and map columns before importing
                    </p>
                    <button
                      onClick={handlePreview}
                      disabled={!file || isLoading}
                      className="btn-primary w-full text-sm  bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-2 rounded-lg font-medium hover:from-blue-700 hover:to-purple-700 transition-all duration-200 shadow-sm hover:shadow disabled:opacity-50 disabled:cursor-not-allowed;"
                    >
                      {isLoading ? 'Processing...' : 'Preview & Map'}
                    </button>
                  </div>
                </div>
              </div>
            )}

            {step === 'preview' && previewData && (
              <div className="space-y-4 md:space-y-6">
                <div className="rounded-lg border border-gray-200 bg-gray-50 p-4">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 md:gap-4">
                    <div>
                      <p className="text-xs md:text-sm text-gray-600">File Source</p>
                      <p className="font-medium text-sm md:text-base">{previewData.source}</p>
                    </div>
                    <div>
                      <p className="text-xs md:text-sm text-gray-600">Rows Detected</p>
                      <p className="font-medium text-sm md:text-base">{previewData.sample_rows.length}</p>
                    </div>
                  </div>
                </div>

                <div>
                  <h4 className="font-medium text-gray-900 mb-3 md:mb-4 text-sm md:text-base">Column Mapping</h4>
                  <div className="space-y-2 md:space-y-3">
                    {['date', 'merchant', 'amount', 'category'].map((field) => (
                      <div key={field} className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                        <span className="font-medium capitalize text-sm">{field}</span>
                        <select
                          value={mapping[field] || ''}
                          onChange={(e) => setMapping({...mapping, [field]: e.target.value})}
                          className="rounded-lg border border-gray-300 px-3 py-2 text-sm w-full sm:w-48"
                        >
                          <option value="">Auto-detect</option>
                          {previewData.columns.map((col: string) => (
                            <option key={col} value={col}>{col}</option>
                          ))}
                        </select>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 className="font-medium text-gray-900 mb-3 md:mb-4 text-sm md:text-base">Preview (First 10 rows)</h4>
                  <div className="overflow-x-auto rounded-lg border border-gray-200 text-xs md:text-sm">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          {previewData.columns.map((col: string) => (
                            <th key={col} className="px-3 py-2 text-left text-xs font-medium text-gray-500 whitespace-nowrap">
                              {col}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-200">
                        {previewData.sample_rows.map((row: any, idx: number) => (
                          <tr key={idx} className="hover:bg-gray-50">
                            {previewData.columns.map((col: string) => (
                              <td key={col} className="px-3 py-2 text-gray-900 max-w-[120px] truncate">
                                {row[col] || '-'}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

                <div className="flex flex-col sm:flex-row justify-end gap-3 pt-4">
                  <button
                    onClick={() => setStep('upload')}
                    className="btn-secondary order-2 sm:order-1 bg-gray-100 text-gray-700 px-4 py-2 rounded-lg font-medium hover:bg-gray-200 transition-all duration-200 border border-gray-300 disabled:opacity-50 disabled:cursor-not-allowed;"
                    disabled={isLoading}
                  >
                    Back
                  </button>
                  <button
                    onClick={handleConfirm}
                    className="btn-primary order-1 sm:order-2  bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-2 rounded-lg font-medium hover:from-blue-700 hover:to-purple-700 transition-all duration-200 shadow-sm hover:shadow disabled:opacity-50 disabled:cursor-not-allowed;"
                    disabled={isLoading}
                  >
                    {isLoading ? 'Confirming...' : 'Confirm Import'}
                  </button>
                </div>
              </div>
            )}

            {step === 'success' && (
              <div className="text-center py-6 md:py-8 lg:py-12">
                <div className="mx-auto mb-4 md:mb-6 flex h-16 w-16 md:h-20 md:w-20 items-center justify-center rounded-full bg-green-100">
                  <CheckCircle className="h-8 w-8 md:h-10 md:w-10 text-green-600" />
                </div>
                <h3 className="mb-2 text-base md:text-xl font-bold text-gray-900">
                  Transactions Imported Successfully!
                </h3>
                <p className="text-sm text-gray-600">
                  Your transactions have been processed and are ready for analysis.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default UploadModal;