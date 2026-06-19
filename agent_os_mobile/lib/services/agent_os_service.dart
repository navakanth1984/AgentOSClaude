import 'dart:convert';
import 'package:http/http.dart' as http;

class AgentOSService {
  final String baseUrl;
  final String apiKey;

  AgentOSService({
    required this.baseUrl,
    required this.apiKey,
  });

  /// Get the standard headers containing the security API Key
  Map<String, String> get _headers => {
    'Content-Type': 'application/json',
    'X-API-Key': apiKey,
  };

  /// Check if the Agent OS server is online and healthy
  Future<Map<String, dynamic>> checkHealth() async {
    final url = Uri.parse('$baseUrl/health');
    try {
      final response = await http.get(url, headers: _headers);
      if (response.statusCode == 200) {
        return jsonDecode(response.body) as Map<String, dynamic>;
      } else {
        return {
          'ok': false,
          'error': 'Server responded with status: ${response.statusCode}'
        };
      }
    } catch (e) {
      return {
        'ok': false,
        'error': 'Connection failed: $e'
      };
    }
  }

  /// Trigger a Swarm research or writing task
  Future<Map<String, dynamic>> runSwarm({
    required String prompt,
    required String mode, // 'screenplay' or 'novelist'
    String? model,
  }) async {
    final payload = {
      'prompt': prompt,
      'mode': mode,
    };
    if (model != null) {
      payload['model'] = model;
    }
    final body = jsonEncode(payload);

    final url = Uri.parse('$baseUrl/swarm');
    try {
      final response = await http.post(url, headers: _headers, body: body);
      if (response.statusCode == 200) {
        return jsonDecode(response.body) as Map<String, dynamic>;
      } else {
        return {
          'success': false,
          'error': 'Swarm failed with status: ${response.statusCode}'
        };
      }
    } catch (e) {
      return {
        'success': false,
        'error': 'Network error: $e'
      };
    }
  }

  /// Translate natural language question into SQL and run query against jobs.db
  Future<Map<String, dynamic>> runSQLQuery({
    required String question,
  }) async {
    final payload = {
      'question': question,
    };
    final body = jsonEncode(payload);

    final url = Uri.parse('$baseUrl/sql');
    try {
      final response = await http.post(url, headers: _headers, body: body);
      if (response.statusCode == 200) {
        return jsonDecode(response.body) as Map<String, dynamic>;
      } else {
        return {
          'success': false,
          'error': 'SQL execution failed with status: ${response.statusCode}'
        };
      }
    } catch (e) {
      return {
        'success': false,
        'error': 'Network error: $e'
      };
    }
  }
}
