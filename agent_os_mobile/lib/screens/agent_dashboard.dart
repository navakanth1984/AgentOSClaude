import 'package:flutter/material.dart';
import '../services/agent_os_service.dart';

class AgentDashboard extends StatefulWidget {
  const AgentDashboard({super.key});

  @override
  State<AgentDashboard> createState() => _AgentDashboardState();
}

class _AgentDashboardState extends State<AgentDashboard> {
  // Configured to point directly to your live online Ngrok tunnel
  final _apiService = AgentOSService(
    baseUrl: 'https://crying-chili-almost.ngrok-free.dev',
    apiKey: 'e84c2337a06d5d5f46406911060bdae59f41ce2c6e276ce87de502ff34526f8b',
  );

  bool _isConnecting = false;
  bool _serverOnline = false;
  String _serverVersion = 'Unknown';
  String _outputText = 'Ready to compile creative swarms...';
  
  final _promptController = TextEditingController();
  String _selectedMode = 'novelist';

  @override
  void initState() {
    super.initState();
    _pingServer();
  }

  Future<void> _pingServer() async {
    setState(() => _isConnecting = true);
    final result = await _apiService.checkHealth();
    setState(() {
      _isConnecting = false;
      _serverOnline = result['ok'] ?? false;
      if (_serverOnline) {
        _serverVersion = result['server_version'] ?? '2.0.0';
        _outputText = 'Connected to Agent OS v$_serverVersion\nVault Note Count: ${result['vault_notes']}';
      } else {
        _outputText = 'Error connecting to server: ${result['error']}';
      }
    });
  }

  String _formatSQLResult(Map<String, dynamic> result) {
    if (result['success'] == false) {
      return '✗ SQL Query Generation/Execution Failed:\n\n'
          'Error: ${result['error']}\n'
          'Generated SQL: ${result['sql'] ?? 'None'}\n'
          'Attempts: ${result['attempts']}';
    }

    final String sql = result['sql'] ?? '';
    final List<dynamic> columns = result['columns'] ?? [];
    final List<dynamic> rows = result['results'] ?? [];
    final int attempts = result['attempts'] ?? 1;

    if (columns.isEmpty) {
      return '✓ Query Executed Successfully (No columns returned).\n\n'
          'SQL: $sql\n'
          'Attempts: $attempts';
    }

    // Format Markdown Table
    final buffer = StringBuffer();
    buffer.writeln('✓ Query Executed Successfully! (Attempts: $attempts)\n');
    buffer.writeln('Generated SQL:');
    buffer.writeln('  $sql\n');
    buffer.writeln('Results:\n');

    // Header row
    buffer.write('| ');
    for (final col in columns) {
      buffer.write('$col | ');
    }
    buffer.writeln();

    // Separator row
    buffer.write('| ');
    for (int i = 0; i < columns.length; i++) {
      buffer.write('--- | ');
    }
    buffer.writeln();

    // Data rows
    if (rows.isEmpty) {
      buffer.writeln('| (No rows returned) |');
    } else {
      for (final row in rows) {
        buffer.write('| ');
        for (final val in row as List<dynamic>) {
          buffer.write('${val ?? "NULL"} | ');
        }
        buffer.writeln();
      }
    }

    return buffer.toString();
  }

  Future<void> _executeSwarm() async {
    if (_promptController.text.isEmpty) return;

    setState(() {
      _isConnecting = true;
      _outputText = _selectedMode == 'sql' 
          ? 'Translating and executing query on backend...'
          : 'Launching Swarm Agents on the backend...';
    });

    Map<String, dynamic> result;
    if (_selectedMode == 'sql') {
      result = await _apiService.runSQLQuery(
        question: _promptController.text,
      );
    } else {
      result = await _apiService.runSwarm(
        prompt: _promptController.text,
        mode: _selectedMode,
      );
    }

    setState(() {
      _isConnecting = false;
      if (_selectedMode == 'sql') {
        _outputText = _formatSQLResult(result);
      } else {
        if (result['success'] == true) {
          _outputText = '✓ Swarm Complete!\n\nSaved Note: ${result['note_path']}\n\nKey Concept:\n${result['output'] ?? 'No text generated.'}';
        } else {
          _outputText = '✗ Swarm Execution Failed:\n${result['error'] ?? 'Unknown error'}';
        }
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F0F1A), // Deep obsidian background
      appBar: AppBar(
        backgroundColor: const Color(0xFF161626),
        title: const Text('Agent OS Mobile', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, color: Colors.cyanAccent),
            onPressed: _pingServer,
          ),
        ],
      ),
      body: _isConnecting
          ? const Center(child: CircularProgressIndicator(valueColor: AlwaysStoppedAnimation(Colors.cyanAccent)))
          : Padding(
              padding: const EdgeInsets.all(16.0),
              child: ListView(
                children: [
                  // Status Header Card
                  Container(
                    padding: const EdgeInsets.all(16.0),
                    decoration: BoxDecoration(
                      color: const Color(0xFF1E1E30),
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: _serverOnline ? Colors.green.withValues(alpha: 0.5) : Colors.red.withValues(alpha: 0.5)),
                    ),
                    child: Row(
                      children: [
                        Icon(
                          _serverOnline ? Icons.cloud_done : Icons.cloud_off,
                          color: _serverOnline ? Colors.green : Colors.red,
                          size: 32,
                        ),
                        const SizedBox(width: 16),
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              _serverOnline ? 'Server Online' : 'Server Offline',
                              style: const TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold),
                            ),
                            Text(
                              'Version: $_serverVersion',
                              style: const TextStyle(color: Colors.grey, fontSize: 14),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 20),

                  // Swarm/SQL Mode Configuration
                  const Text('Select Operation Mode', style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.w600)),
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 16,
                    runSpacing: 8,
                    children: [
                      Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Radio<String>(
                            value: 'novelist',
                            groupValue: _selectedMode,
                            activeColor: Colors.cyanAccent,
                            onChanged: (val) => setState(() => _selectedMode = val!),
                          ),
                          const Text('Novelist Swarm', style: TextStyle(color: Colors.white)),
                        ],
                      ),
                      Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Radio<String>(
                            value: 'screenplay',
                            groupValue: _selectedMode,
                            activeColor: Colors.cyanAccent,
                            onChanged: (val) => setState(() => _selectedMode = val!),
                          ),
                          const Text('Screenplay Swarm', style: TextStyle(color: Colors.white)),
                        ],
                      ),
                      Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Radio<String>(
                            value: 'sql',
                            groupValue: _selectedMode,
                            activeColor: Colors.cyanAccent,
                            onChanged: (val) => setState(() => _selectedMode = val!),
                          ),
                          const Text('SQL Query', style: TextStyle(color: Colors.white)),
                        ],
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
 
                   // Prompt Entry Input Box
                   TextField(
                     controller: _promptController,
                     style: const TextStyle(color: Colors.white),
                     decoration: InputDecoration(
                       hintText: _selectedMode == 'sql'
                           ? 'Ask a database question (e.g., "how many failed jobs are there?")'
                           : 'Enter creative concept details...',
                       hintStyle: const TextStyle(color: Colors.grey),
                       filled: true,
                       fillColor: const Color(0xFF1E1E30),
                       border: OutlineInputBorder(
                         borderRadius: BorderRadius.circular(12),
                         borderSide: BorderSide.none,
                       ),
                       focusedBorder: OutlineInputBorder(
                         borderRadius: BorderRadius.circular(12),
                         borderSide: const BorderSide(color: Colors.cyanAccent),
                       ),
                     ),
                     maxLines: 4,
                   ),
                   const SizedBox(height: 16),
 
                   // Launch/Run Button
                   ElevatedButton(
                     style: ElevatedButton.styleFrom(
                       backgroundColor: Colors.cyanAccent,
                       foregroundColor: Colors.black,
                       padding: const EdgeInsets.symmetric(vertical: 16),
                       shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                     ),
                     onPressed: _executeSwarm,
                     child: Text(
                       _selectedMode == 'sql' ? 'Run Query' : 'Launch Swarm',
                       style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                     ),
                   ),
                  const SizedBox(height: 24),

                  // Console/Output Log Panel
                  const Text('Execution Output', style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.w600)),
                  const SizedBox(height: 10),
                  Container(
                    padding: const EdgeInsets.all(16),
                    constraints: const BoxConstraints(minHeight: 200),
                    decoration: BoxDecoration(
                      color: const Color(0xFF161626),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: Colors.white.withValues(alpha: 0.1)),
                    ),
                    child: SingleChildScrollView(
                      child: Text(
                        _outputText,
                        style: const TextStyle(color: Colors.cyanAccent, fontFamily: 'monospace', fontSize: 13),
                      ),
                    ),
                  ),
                ],
              ),
            ),
    );
  }
}
