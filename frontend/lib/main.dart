import 'package:flutter/material.dart';
import 'package:frontend/screens/debug_screen.dart';

import 'package:logging/logging.dart';

void main() async {
  // Configure logging
  Logger.root.onRecord.listen((record) {
    debugPrint('${record.level.name}: ${record.time}: ${record.message}');
  });

  // TODO: Added a ping-pong test to check if the server is running
  // TODO: Add button to fetch data from the server
  // TODO: Add graph to display the data (offline and online)

  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Lokomat FES Server Interface',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      initialRoute: DebugScreen.route,
      routes: {
        DebugScreen.route: (context) => const DebugScreen(),
      },
    );
  }
}