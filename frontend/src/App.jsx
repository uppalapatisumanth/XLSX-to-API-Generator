import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Upload, FileText, Code, CheckCircle, AlertCircle, Loader2, Download, HelpCircle, X, Sparkles, Zap, LayoutTemplate } from 'lucide-react';

function App() {
    const [file, setFile] = useState(null);
    const [taskId, setTaskId] = useState(null);
    const [stage, setStage] = useState('upload'); // upload, processing, completed
    const [logs, setLogs] = useState([]);
    const [artifacts, setArtifacts] = useState([]);
    const [error, setError] = useState(null);
    const [showGuide, setShowGuide] = useState(false);

    const handleFileChange = (e) => {
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0]);
        }
    };

    const uploadFile = async () => {
        if (!file) return;

        setStage('processing');
        setLogs(['Starting upload...']);
        setError(null);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await axios.post('/api/upload', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            setTaskId(response.data.task_id);
        } catch (err) {
            setError('Upload failed: ' + (err.response?.data?.detail || err.message));
            setStage('upload');
        }
    };

    useEffect(() => {
        let interval;
        if (taskId && stage === 'processing') {
            interval = setInterval(async () => {
                try {
                    const res = await axios.get(`/api/status/${taskId}`);
                    setLogs(res.data.logs);

                    if (res.data.status === 'completed') {
                        setStage('completed');
                        setArtifacts({
                            files: res.data.artifacts_ready,
                            preview: res.data.api_preview
                        });
                        clearInterval(interval);
                    } else if (res.data.status === 'failed') {
                        setStage('upload'); // OR completed with error
                        setError("Processing failed. Check logs.");
                        clearInterval(interval);
                    }
                } catch (err) {
                    console.error("Polling error", err);
                }
            }, 1000);
        }
        return () => clearInterval(interval);
    }, [taskId, stage]);

    const downloadFile = (type) => {
        window.open(`/api/download/${taskId}/${type}`, '_blank');
    };

    return (
        <div className="min-h-screen relative overflow-hidden font-sans text-slate-800 selection:bg-pink-300 selection:text-pink-900">
            {/* Full Screen Animated Aesthetic Background */}
            <div className="fixed inset-0 bg-[conic-gradient(at_top_right,_var(--tw-gradient-stops))] from-indigo-200 via-slate-100 to-indigo-200 opacity-40 -z-10"></div>
            <div className="fixed inset-0 bg-[radial-gradient(ellipse_at_top_left,_var(--tw-gradient-stops))] from-purple-300 via-pink-300 to-transparent blur-3xl opacity-30 -z-10"></div>
            <div className="fixed inset-0 bg-[radial-gradient(ellipse_at_bottom_right,_var(--tw-gradient-stops))] from-cyan-300 via-blue-200 to-transparent blur-3xl opacity-30 -z-10"></div>

            {/* Glass Navbar */}
            <header className="fixed top-0 w-full z-50 px-6 py-4">
                <nav className="mx-auto max-w-6xl bg-white/40 backdrop-blur-xl border border-white/40 shadow-sm rounded-2xl px-6 py-3 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="bg-gradient-to-tr from-violet-600 to-indigo-600 text-white p-2 rounded-lg shadow-lg shadow-indigo-500/30">
                            <Zap className="w-5 h-5 fill-current" />
                        </div>
                        <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-violet-600 to-indigo-600">
                            API Factory
                        </span>
                    </div>
                    <button
                        onClick={() => setShowGuide(true)}
                        className="flex items-center gap-2 px-4 py-2 text-sm font-semibold text-slate-600 hover:text-slate-900 bg-white/50 hover:bg-white/80 rounded-full transition-all border border-transparent hover:border-slate-200"
                    >
                        <LayoutTemplate className="w-4 h-4" />
                        <span>Guide</span>
                    </button>
                </nav>
            </header>

            <main className="container mx-auto max-w-4xl pt-32 pb-12 px-6 relative z-10 flex flex-col items-center justify-center min-h-[80vh]">

                {/* Upload Stage - Aesthetic Card */}
                <div className={`w-full transition-all duration-700 ease-out transform ${stage !== 'upload' ? 'hidden scale-95 opacity-0' : 'scale-100 opacity-100'}`}>
                    <div className="bg-white/60 backdrop-blur-2xl border border-white/60 shadow-[0_8px_32px_0_rgba(31,38,135,0.07)] rounded-3xl p-10 md:p-14 text-center">
                        <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-tr from-pink-100 to-violet-100 rounded-[2rem] mb-6 text-violet-600 shadow-sm rotate-3">
                            <Sparkles className="w-10 h-10" />
                        </div>
                        <h1 className="text-4xl md:text-5xl font-black text-slate-800 mb-4 tracking-tight">
                            Build APIs <span className="text-transparent bg-clip-text bg-gradient-to-r from-violet-600 to-pink-600">Beautifully.</span>
                        </h1>
                        <p className="text-lg text-slate-500 mb-10 max-w-lg mx-auto leading-relaxed">
                            Drop your definition file and watch the magic happen. We generate production-ready collections instantly.
                        </p>

                        <div className="relative group max-w-xl mx-auto">
                            <div className="absolute -inset-1 bg-gradient-to-r from-violet-600 to-pink-600 rounded-2xl blur opacity-25 group-hover:opacity-50 transition duration-1000 group-hover:duration-200"></div>
                            <div className="relative bg-white/80 backdrop-blur-sm border-2 border-dashed border-slate-300 hover:border-violet-400 rounded-2xl p-12 transition-all cursor-pointer">
                                <input
                                    type="file"
                                    accept=".xlsx"
                                    onChange={handleFileChange}
                                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-20"
                                />
                                <div className="flex flex-col items-center gap-4">
                                    <div className="p-4 bg-slate-50 rounded-full text-slate-400 group-hover:text-violet-600 group-hover:bg-violet-50 transition-colors">
                                        <Upload className="w-8 h-8" />
                                    </div>
                                    <div className="flex flex-col">
                                        <span className="font-bold text-lg text-slate-700 group-hover:text-violet-700 transition-colors">
                                            {file ? file.name : "Click to Upload Spec"}
                                        </span>
                                        <span className="text-sm text-slate-400 font-medium">.xlsx format supported</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {error && (
                            <div className="mt-8 p-4 bg-red-50/80 backdrop-blur-sm border border-red-100 text-red-600 rounded-2xl inline-flex items-center gap-2 text-sm font-medium animate-in fade-in slide-in-from-bottom-2">
                                <AlertCircle className="w-4 h-4" />
                                {error}
                            </div>
                        )}

                        <div className="mt-10">
                            <button
                                onClick={uploadFile}
                                disabled={!file}
                                className={`group relative inline-flex items-center justify-center px-8 py-4 font-bold text-white transition-all duration-200 bg-slate-900 rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-slate-900 ${!file ? 'opacity-50 cursor-not-allowed' : 'hover:bg-slate-800 hover:shadow-xl hover:-translate-y-1'}`}
                            >
                                <span className="mr-2 text-lg">Generate Artifacts</span>
                                <Zap className="w-5 h-5 group-hover:text-yellow-400 transition-colors" />
                            </button>
                        </div>

                        <div className="mt-6">
                            <a href="http://localhost:8000/api/template" target="_blank" className="text-sm font-semibold text-slate-400 hover:text-violet-600 transition-colors inline-flex items-center gap-1">
                                <Download className="w-3 h-3" />
                                Get Template
                            </a>
                        </div>
                    </div>
                </div>

                {/* Processing Stage - Minimalist Loader */}
                <div className={`w-full max-w-2xl bg-white/60 backdrop-blur-2xl border border-white/60 shadow-[0_8px_32px_0_rgba(31,38,135,0.07)] rounded-3xl p-10 text-center transition-all ${stage === 'processing' ? 'block animate-in fade-in scale-95 duration-500' : 'hidden'}`}>
                    <div className="flex justify-center mb-8">
                        <div className="relative w-24 h-24">
                            <div className="absolute inset-0 border-4 border-slate-100 rounded-full"></div>
                            <div className="absolute inset-0 border-4 border-violet-600 rounded-full border-t-transparent animate-spin"></div>
                            <div className="absolute inset-0 flex items-center justify-center">
                                <Sparkles className="w-8 h-8 text-violet-600 animate-pulse" />
                            </div>
                        </div>
                    </div>
                    <h2 className="text-2xl font-bold text-slate-800 mb-2">Weaving Code...</h2>
                    <p className="text-slate-500 mb-8">Analyzing patterns and generating suites.</p>

                    <div className="bg-slate-900/90 backdrop-blur text-left rounded-2xl p-6 h-64 overflow-y-auto font-mono text-xs shadow-inner">
                        {logs.map((log, i) => (
                            <div key={i} className="mb-2 flex gap-3 text-slate-300">
                                <span className="text-violet-400 shrink-0">➜</span>
                                <span className="opacity-90">{log}</span>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Completion Stage - Success Dashboard */}
                <div className={`w-full bg-white/70 backdrop-blur-2xl border border-white/60 shadow-[0_8px_32px_0_rgba(31,38,135,0.07)] rounded-[2rem] p-8 md:p-12 transition-all ${stage === 'completed' ? 'block animate-in fade-in slide-in-from-bottom-8 duration-700' : 'hidden'}`}>

                    <div className="flex flex-col md:flex-row items-center justify-between mb-8 gap-4">
                        <div className="flex items-center gap-4">
                            <div className="w-14 h-14 bg-emerald-100 text-emerald-600 rounded-2xl flex items-center justify-center shadow-sm rotate-3">
                                <CheckCircle className="w-7 h-7" />
                            </div>
                            <div>
                                <h2 className="text-2xl font-black text-slate-800">Ready to Ship</h2>
                                <p className="text-slate-500 font-medium">Generation complete.</p>
                            </div>
                        </div>
                        <button
                            onClick={() => { setStage('upload'); setFile(null); setLogs([]); setTaskId(null); }}
                            className="px-5 py-2.5 bg-white border border-slate-200 hover:border-violet-300 hover:text-violet-700 text-slate-600 font-bold rounded-xl text-sm transition-all shadow-sm"
                        >
                            Start Over
                        </button>
                    </div>

                    {/* Preview Section */}
                    {artifacts.preview && artifacts.preview.length > 0 && (
                        <div className="mb-10 overflow-hidden rounded-2xl border border-slate-200/60 bg-white/50">
                            <div className="px-6 py-4 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
                                <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Blueprint Preview</span>
                                <span className="text-xs font-bold bg-slate-200 text-slate-600 px-2 py-1 rounded-md">{artifacts.preview.length} Endpoints</span>
                            </div>
                            <div className="overflow-x-auto max-h-[300px]">
                                <table className="min-w-full text-left text-sm whitespace-nowrap">
                                    <tbody className="divide-y divide-slate-100">
                                        {artifacts.preview.map((api, idx) => (
                                            <tr key={idx} className="hover:bg-violet-50/30 transition-colors group">
                                                <td className="px-6 py-3 font-mono text-[10px] text-slate-400 group-hover:text-violet-400">{api.ref_id}</td>
                                                <td className="px-6 py-3">
                                                    <span className={`px-2 py-1 rounded-md text-[10px] font-black uppercase tracking-wider shadow-sm ${api.method === 'GET' ? 'bg-blue-500 text-white' :
                                                        api.method === 'POST' ? 'bg-emerald-500 text-white' :
                                                            api.method === 'DELETE' ? 'bg-rose-500 text-white' :
                                                                'bg-amber-500 text-white'
                                                        }`}>
                                                        {api.method}
                                                    </span>
                                                </td>
                                                <td className="px-6 py-3 font-bold text-slate-700">{api.name}</td>
                                                <td className="px-6 py-3 font-mono text-xs text-slate-500">{api.url}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    )}

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <button onClick={() => downloadFile('postman')} className="group relative overflow-hidden rounded-2xl bg-gradient-to-br from-orange-500 to-orange-600 p-1 text-white shadow-lg shadow-orange-200 transition-all hover:scale-[1.02] hover:shadow-orange-300">
                            <div className="relative flex h-full flex-col justify-between bg-white bg-opacity-10 backdrop-blur-sm p-6">
                                <div className="mb-4 text-orange-100">
                                    <img src="https://www.vectorlogo.zone/logos/getpostman/getpostman-icon.svg" className="w-8 h-8 opacity-90 invert grayscale brightness-200" alt="Postman" />
                                </div>
                                <div>
                                    <h3 className="text-xl font-bold">Postman Collection</h3>
                                    <p className="text-orange-100 text-sm mt-1 opacity-80">Download JSON 2.1</p>
                                </div>
                            </div>
                        </button>

                        <button onClick={() => downloadFile('pytest')} className="group relative overflow-hidden rounded-2xl bg-gradient-to-br from-slate-800 to-slate-900 p-1 text-white shadow-lg shadow-slate-300 transition-all hover:scale-[1.02] hover:shadow-slate-400">
                            <div className="relative flex h-full flex-col justify-between bg-white bg-opacity-5 backdrop-blur-sm p-6">
                                <div className="mb-4 text-emerald-300">
                                    <FileText className="w-8 h-8" />
                                </div>
                                <div>
                                    <h3 className="text-xl font-bold">Pytest Suite</h3>
                                    <p className="text-slate-400 text-sm mt-1">Download ZIP</p>
                                </div>
                            </div>
                        </button>
                    </div>
                </div>
            </main>

            {/* Aesthetic Guide Modal */}
            {showGuide && (
                <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
                    <div className="absolute inset-0 bg-slate-900/60 backdrop-blur-md" onClick={() => setShowGuide(false)} />
                    <div
                        className="relative w-full max-w-4xl bg-white rounded-3xl shadow-2xl overflow-hidden animate-in zoom-in-95 duration-300 flex flex-col max-h-[90vh]"
                        onClick={(e) => e.stopPropagation()}
                    >
                        <div className="flex items-center justify-between p-8 bg-slate-50 border-b border-slate-100 flex-shrink-0">
                            <div>
                                <h3 className="text-2xl font-black text-slate-800">The Manual</h3>
                                <p className="text-slate-500 text-sm font-medium">How to structure your .xlsx file</p>
                            </div>
                            <button onClick={() => setShowGuide(false)} className="p-2 bg-white rounded-full text-slate-400 hover:text-slate-900 shadow-sm border border-slate-100 transition-all">
                                <X className="w-6 h-6" />
                            </button>
                        </div>
                        <div className="p-8 overflow-y-auto prose max-w-none flex-grow">
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                                <div className="col-span-1">
                                    <div className="sticky top-0 space-y-4">
                                        <div
                                            onClick={() => window.open('http://localhost:8000/api/template', '_blank')}
                                            className="p-4 rounded-2xl bg-indigo-50 border border-indigo-100 text-indigo-900 cursor-pointer hover:bg-indigo-100 hover:scale-[1.02] transition-all group"
                                        >
                                            <div className="flex justify-between items-start">
                                                <span className="block text-xs font-bold uppercase tracking-wider opacity-60 mb-1">REQ 01</span>
                                                <Download className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" />
                                            </div>
                                            <span className="font-bold block">Two Sheets</span>
                                            <p className="text-sm opacity-80 mt-1">Ensure your file has exact sheet names.</p>
                                        </div>
                                        <div
                                            onClick={() => window.open('http://localhost:8000/api/template', '_blank')}
                                            className="p-4 rounded-2xl bg-white border border-slate-100 text-slate-600 shadow-sm cursor-pointer hover:border-indigo-300 hover:shadow-md hover:scale-[1.02] transition-all group"
                                        >
                                            <div className="flex justify-between items-start">
                                                <span className="block text-xs font-bold uppercase tracking-wider opacity-60 mb-1 group-hover:text-indigo-500">REQ 02</span>
                                                <Download className="w-4 h-4 text-indigo-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                                            </div>
                                            <span className="font-bold group-hover:text-indigo-600 block">Consistent Headers</span>
                                            <p className="text-sm opacity-80 mt-1">Don't rename columns.</p>
                                        </div>

                                        <div className="pt-4">
                                            <button
                                                onClick={() => window.open('http://localhost:8000/api/template', '_blank')}
                                                className="w-full py-3 px-4 bg-slate-900 text-white rounded-xl font-bold text-sm hover:bg-slate-800 transition-all flex items-center justify-center gap-2 shadow-lg shadow-slate-200"
                                            >
                                                <Download className="w-4 h-4" />
                                                Download Template
                                            </button>
                                        </div>
                                    </div>
                                </div>
                                <div className="col-span-2 space-y-8">
                                    <div>
                                        <h4 className="flex items-center gap-2 text-lg font-bold text-slate-800">
                                            <span className="flex items-center justify-center w-6 h-6 rounded-full bg-indigo-600 text-white text-xs">1</span>
                                            sheet: 'environments'
                                        </h4>
                                        <div className="mt-4 bg-slate-900 rounded-xl p-4 text-slate-300 text-sm font-mono overflow-x-auto shadow-inner">
                                            <div className="flex gap-8 border-b border-slate-700 pb-2 mb-2 text-slate-500 uppercase text-xs font-bold">
                                                <span>A: Variable</span>
                                                <span>B: Value</span>
                                            </div>
                                            <div className="flex gap-8">
                                                <span>base_url</span>
                                                <span className="text-emerald-400">https://api.myapp.com</span>
                                            </div>
                                        </div>
                                    </div>

                                    <div>
                                        <h4 className="flex items-center gap-2 text-lg font-bold text-slate-800">
                                            <span className="flex items-center justify-center w-6 h-6 rounded-full bg-indigo-600 text-white text-xs">2</span>
                                            sheet: 'apis'
                                        </h4>
                                        <div className="mt-4 border border-slate-200 rounded-xl overflow-hidden shadow-sm">
                                            <table className="w-full text-sm">
                                                <thead className="bg-slate-50 text-slate-500 font-semibold text-xs uppercase">
                                                    <tr>
                                                        <th className="px-4 py-3 text-left">Column</th>
                                                        <th className="px-4 py-3 text-left">Description</th>
                                                    </tr>
                                                </thead>
                                                <tbody className="divide-y divide-slate-100">
                                                    <tr><td className="px-4 py-2 font-mono text-purple-600 selection:bg-purple-100">Module/Feature</td><td className="px-4 py-2 text-slate-600">Folder grouping name.</td></tr>
                                                    <tr><td className="px-4 py-2 font-mono text-purple-600 selection:bg-purple-100">API Name</td><td className="px-4 py-2 text-slate-600">Unique Request identifier.</td></tr>
                                                    <tr><td className="px-4 py-2 font-mono text-purple-600 selection:bg-purple-100">HTTP Method</td><td className="px-4 py-2 text-slate-600">GET/POST/PUT/DELETE</td></tr>
                                                    <tr><td className="px-4 py-2 font-mono text-purple-600 selection:bg-purple-100">Endpoint URL</td><td className="px-4 py-2 text-slate-600">Relative path (e.g. /v1/login).</td></tr>
                                                    <tr><td className="px-4 py-2 font-mono text-purple-600 selection:bg-purple-100">Headers Required</td><td className="px-4 py-2 text-slate-600">JSON format or Key:Value.</td></tr>
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default App;
