// src/app/page.tsx
'use client';

import { useState, useRef } from 'react';
import { Upload, FileAudio, Loader2, CheckCircle, XCircle, Clock, Play } from 'lucide-react';

interface JobResponse {
  job_id: string;
  status: string;
}

interface JobResult {
  jobId: string;
  keyName: string;
  createdAt: string;
  errorMessage: string;
  status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED';
  summaryResult?: string;
}

interface SummaryData {
  summary: string;
  bulletPoints: string[];
  topicIdentification: string[];
  quoteExtraction: string[];
  characterIdentification: string[];
  sentimentAnalysis: {
    sentiment: string;
    description: string;
  };
  qna: Array<{
    question: string;
    answer: string;
  }>;
  namedEntities: {
    people: string[];
    places: string[];
    organizations: string[];
  };
  contentClassification: {
    type: string;
    characteristics: string[];
  };
}

export default function AudioSummarizer() {
  const [file, setFile] = useState<File | null>(null);
  const [jobId, setJobId] = useState<string>('');
  const [status, setStatus] = useState<string>('');
  const [isUploading, setIsUploading] = useState(false);
  const [isPolling, setIsPolling] = useState(false);
  const [summaryData, setSummaryData] = useState<SummaryData | null>(null);
  const [error, setError] = useState<string>('');
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Backend base URL - adjust this to match your backend
  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile) {
      if (selectedFile.type === 'audio/mpeg' || selectedFile.name.endsWith('.mp3')) {
        setFile(selectedFile);
        setError('');
        // Clear previous results
        setJobId('');
        setStatus('');
        setSummaryData(null);
      } else {
        setError('Please select an MP3 file');
        setFile(null);
      }
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const droppedFiles = e.dataTransfer.files;
    if (droppedFiles.length > 0) {
      const droppedFile = droppedFiles[0];
      if (droppedFile.type === 'audio/mpeg' || droppedFile.name.endsWith('.mp3')) {
        setFile(droppedFile);
        setError('');
        // Clear previous results
        setJobId('');
        setStatus('');
        setSummaryData(null);
      } else {
        setError('Please select an MP3 file');
      }
    }
  };

  const uploadFile = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    setIsUploading(true);
    setError('');

    try {
      // STEP 1: Get presigned URL from backend
      const keyName = file.name;
      const presignedResponse = await fetch(`${API_BASE_URL}/get-presigned-url`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ keyName }),
      });

      if (!presignedResponse.ok) {
        throw new Error('Failed to get presigned URL');
      }

      const { url, keyName: newKeyName } = await presignedResponse.json();

      // STEP 2: Upload file directly to MinIO using the presigned URL
      const uploadResponse = await fetch(url, {
        method: 'PUT',
        headers: {
          'Content-Type': file.type,
        },
        body: file,
      });

      if (!uploadResponse.ok) {
        throw new Error('Upload to MinIO failed');
      }

      // STEP 3: Notify backend that upload is done and start processing
      const summaryResponse = await fetch(`${API_BASE_URL}/send-summary-request?file=${encodeURIComponent(newKeyName)}`, {
        method: 'POST',
      });

      if (!summaryResponse.ok) {
        throw new Error('Failed to send summary request');
      }

      const result: JobResponse = await summaryResponse.json();
      console.log("SUMMARY_RESULT:", result);
      setJobId(result.job_id);
      setStatus(result.status);

      // STEP 4: Start polling for results
      startPolling(result.job_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setIsUploading(false);
    }
  };

  const startPolling = (jobId: string) => {
    setIsPolling(true);
    
    const pollResult = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/result?jobId=${jobId}`);
        console.log(`POLL_RESPONSE FOR JOB ID ${jobId}: ${response}"`)
        if (!response.ok) {
          if (response.status === 404) {
            // Job not found yet, continue polling
            return;
          }
          throw new Error(`Failed to get result: ${response.statusText}`);
        }

        const result: JobResult = await response.json();
        console.log("JOB_RESULT", result)
        setStatus(result.status);

        if (result.status === 'COMPLETED') {
          if (result.summaryResult) {
            try {
              const parsedSummary: SummaryData = JSON.parse(JSON.parse(result.summaryResult));
              console.log("BULLET_POINTS", parsedSummary.bulletPoints)
              console.log("TYPE_BRUH: ", typeof parsedSummary)
              console.log("TYPE_BRUH2: ", typeof result.summaryResult)
              
              setSummaryData(parsedSummary);
              console.log("SUMMARY_DATA", summaryData)
            } catch (parseError) {
              console.log(parseError instanceof Error ? parseError.message : "Failed to parse result")
              setError('Failed to parse summary result');
            }
          }
          stopPolling();
        } else if (result.status === 'FAILED') {
          setError(result.errorMessage || 'Processing failed');
          stopPolling();
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to get result');
        stopPolling();
      }
    };

    // Poll immediately, then every 2 seconds
    pollResult();
    pollingIntervalRef.current = setInterval(pollResult, 2000);
  };

  const stopPolling = () => {
    setIsPolling(false);
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
      pollingIntervalRef.current = null;
    }
  };

  const resetApp = () => {
    setFile(null);
    setJobId('');
    setStatus('');
    setSummaryData(null);
    setError('');
    setIsDragOver(false);
    stopPolling();
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'PENDING':
        return <Clock className="w-5 h-5 text-yellow-500" />;
      case 'PROCESSING':
        return <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />;
      case 'COMPLETED':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'FAILED':
        return <XCircle className="w-5 h-5 text-red-500" />;
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Audio Summarizer</h1>
          <p className="text-gray-600">Upload your MP3 file and get an AI-powered summary</p>
        </div>

        {/* Upload Section */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
          <div 
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
              isDragOver 
                ? 'border-blue-500 bg-blue-50' 
                : 'border-gray-300 hover:border-gray-400'
            }`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <FileAudio className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            
            <input
              ref={fileInputRef}
              type="file"
              accept=".mp3,audio/mpeg"
              onChange={handleFileSelect}
              className="hidden"
              id="file-upload"
            />
            
            <div className="mb-4">
              <p className="text-lg font-medium text-gray-700 mb-2">
                {isDragOver ? 'Drop your MP3 file here' : 'Drag & drop your MP3 file here'}
              </p>
              <p className="text-sm text-gray-500">or</p>
            </div>
            
            <label
              htmlFor="file-upload"
              className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 cursor-pointer transition-colors"
            >
              <Upload className="w-4 h-4 mr-2" />
              Select MP3 File
            </label>
            
            {file && (
              <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-700">
                  Selected: <span className="font-medium">{file.name}</span>
                </p>
                <p className="text-xs text-gray-500">
                  Size: {(file.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
            )}
          </div>

          <div className="flex gap-4 mt-6">
            <button
              onClick={uploadFile}
              disabled={!file || isUploading || isPolling}
              className="flex-1 bg-green-600 text-white py-3 px-6 rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
            >
              {isUploading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Uploading...
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 mr-2" />
                  Generate Summary
                </>
              )}
            </button>
            
            <button
              onClick={resetApp}
              className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Reset
            </button>
          </div>
        </div>

        {/* Status Section */}
        {jobId && (
          <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4 text-gray-900">Processing Status</h2>
            <div className="flex items-center gap-3">
              {getStatusIcon()}
              <span className="font-medium capitalize">{status.toLowerCase()}</span>
              {isPolling && <span className="text-sm text-gray-500">(Checking for updates...)</span>}
            </div>
            <p className="text-sm text-gray-600 mt-2">Job ID: {jobId}</p>
          </div>
        )}

        {/* Error Section */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-6">
            <div className="flex items-center gap-2">
              <XCircle className="w-5 h-5 text-red-500" />
              <span className="font-medium text-red-800">Error</span>
            </div>
            <p className="text-red-700 mt-1">{error}</p>
          </div>
        )}

        {/* Summary Results */}
        {summaryData && (
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-2xl font-bold mb-6 text-gray-900">Summary Results</h2>
            
            {/* Main Summary */}
            {summaryData.summary && (
              <div className="mb-8">
                <h3 className="text-lg font-semibold mb-3 text-gray-800">Summary</h3>
                <p className="text-gray-700 leading-relaxed bg-gray-50 p-4 rounded-lg">
                  {summaryData.summary}
                </p>
              </div>
            )}

            {/* Bullet points */}
            {summaryData.bulletPoints && summaryData.bulletPoints.length > 0 && (
              <div className="mb-6">
                <h3 className="text-lg font-semibold mb-3 text-gray-800">Bullet Points</h3>
                <div className="grid gap-2">
                  {summaryData.bulletPoints.map((topic, index) => (
                    <div key={index} className="bg-orange-50 p-3 rounded-lg">
                      <p className="text-gray-700">{topic}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Topics */}
            {summaryData.topicIdentification && summaryData.topicIdentification.length > 0 && (
              <div className="mb-6">
                <h3 className="text-lg font-semibold mb-3 text-gray-800">Key Topics</h3>
                <div className="grid gap-2">
                  {summaryData.topicIdentification.map((topic, index) => (
                    <div key={index} className="bg-blue-50 p-3 rounded-lg">
                      <p className="text-gray-700">{topic}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Quotes */}
            {summaryData.quoteExtraction && summaryData.quoteExtraction.length > 0 && (
              <div className="mb-6">
                <h3 className="text-lg font-semibold mb-3 text-gray-800">Notable Quotes</h3>
                <div className="grid gap-3">
                  {summaryData.quoteExtraction.map((quote, index) => (
                    <blockquote key={index} className="border-l-4 border-green-500 pl-4 italic text-gray-700 bg-green-50 p-3 rounded-r-lg">
                      {quote}
                    </blockquote>
                  ))}
                </div>
              </div>
            )}

            {/* Character Identification */}
            {summaryData.characterIdentification && summaryData.characterIdentification.length > 0 && (
              <div className="mb-6">
                <h3 className="text-lg font-semibold mb-3 text-gray-800">Characters</h3>
                <div className="grid gap-2">
                  {summaryData.characterIdentification.map((character, index) => (
                    <div key={index} className="bg-pink-50 p-3 rounded-lg">
                      <p className="text-gray-700">{character}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Sentiment Analysis */}
            {summaryData.sentimentAnalysis && (
              <div className="mb-6">
                <h3 className="text-lg font-semibold mb-3 text-gray-800">Sentiment Analysis</h3>
                <div className="bg-purple-50 p-4 rounded-lg">
                  {summaryData.sentimentAnalysis.sentiment && (
                    <p className="font-medium text-purple-800 capitalize">
                      {summaryData.sentimentAnalysis.sentiment}
                    </p>
                  )}
                  {summaryData.sentimentAnalysis.description && (
                    <p className="text-gray-700 mt-1">{summaryData.sentimentAnalysis.description}</p>
                  )}
                </div>
              </div>
            )}

            {/* Named Entities */}
            {summaryData.namedEntities && (
              <div className="mb-6">
                <h3 className="text-lg font-semibold mb-3 text-gray-800">Named Entities</h3>
                <div className="grid md:grid-cols-2 gap-4">
                  {summaryData.namedEntities.people && summaryData.namedEntities.people.length > 0 && (
                    <div>
                      <h4 className="font-medium text-gray-700 mb-2">People</h4>
                      <div className="flex flex-wrap gap-2">
                        {summaryData.namedEntities.people.map((person, index) => (
                          <span key={index} className="bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full text-sm">
                            {person}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  {summaryData.namedEntities.places && summaryData.namedEntities.places.length > 0 && (
                    <div>
                      <h4 className="font-medium text-gray-700 mb-2">Places</h4>
                      <div className="flex flex-wrap gap-2">
                        {summaryData.namedEntities.places.map((place, index) => (
                          <span key={index} className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-sm">
                            {place}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  {summaryData.namedEntities.organizations && summaryData.namedEntities.organizations.length > 0 && (
                    <div>
                      <h4 className="font-medium text-gray-700 mb-2">Organizations</h4>
                      <div className="flex flex-wrap gap-2">
                        {summaryData.namedEntities.organizations.map((org, index) => (
                          <span key={index} className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-sm">
                            {org}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Q&A */}
            {summaryData.qna && summaryData.qna.length > 0 && (
              <div className="mb-6">
                <h3 className="text-lg font-semibold mb-3 text-gray-800">Questions & Answers</h3>
                <div className="space-y-4">
                  {summaryData.qna.map((qa, index) => (
                    <div key={index} className="bg-gray-50 p-4 rounded-lg">
                      {qa.question && (
                        <p className="font-medium text-gray-800 mb-2">Q: {qa.question}</p>
                      )}
                      {qa.answer && (
                        <p className="text-gray-700">A: {qa.answer}</p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Content Classification */}
            {summaryData.contentClassification && (
              <div>
                <h3 className="text-lg font-semibold mb-3 text-gray-800">Content Classification</h3>
                <div className="bg-indigo-50 p-4 rounded-lg">
                  {summaryData.contentClassification.type && (
                    <p className="font-medium text-indigo-800 mb-2">{summaryData.contentClassification.type}</p>
                  )}
                  {summaryData.contentClassification.characteristics && summaryData.contentClassification.characteristics.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                      {summaryData.contentClassification.characteristics.map((char, index) => (
                        <span key={index} className="bg-indigo-100 text-indigo-700 px-2 py-1 rounded-full text-sm">
                          {char}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}