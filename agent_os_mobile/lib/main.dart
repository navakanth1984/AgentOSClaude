import 'package:flutter/material.dart';
import 'screens/agent_dashboard.dart';

void main() {
  runApp(const AgentOSApp());
}

class AgentOSApp extends StatelessWidget {
  const AgentOSApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Agent OS Client',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.cyanAccent,
          brightness: Brightness.dark,
        ),
        useMaterial3: true,
      ),
      home: const AgentDashboard(),
    );
  }
}
