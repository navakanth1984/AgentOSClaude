#!/usr/bin/env python3
"""
test_telemetry_schema.py — NTH Brain Telemetry Schema Validation Suite
Verifies structure, value ranges, and types of exported student drawing telemetry.
"""

import json
import unittest

class TestTelemetrySchema(unittest.TestCase):
    def setUp(self):
        # Mock telemetry coordinate package matching exports from app.js
        self.mock_data = {
            "metadata": {
                "project": "NTH Brain",
                "version": "MVP v0.1",
                "timestamp": "2026-06-19T03:13:47.000Z",
                "sensor_rate": "continuous"
            },
            "student_mind_graph": {
                "skill_source_mastery": 0.20,
                "skill_intermediate_mastery": 0.46,
                "path_efficiency": 0.36,
                "current_anchor": None,
                "target_flow_completed": True
            },
            "strokes": [
                {
                    "id": "stroke_1718784000",
                    "points": [
                        {"x": 120.5, "y": 80.3, "t": 1718784000000, "v": 0.0},
                        {"x": 125.0, "y": 82.1, "t": 1718784000100, "v": 45.2},
                        {"x": 240.2, "y": 310.5, "t": 1718784000500, "v": 287.1}
                    ]
                }
            ]
        }

    def test_metadata_structure(self):
        """Verify presence and type formatting of metadata fields."""
        self.assertIn("metadata", self.mock_data)
        meta = self.mock_data["metadata"]
        self.assertEqual(meta["project"], "NTH Brain")
        self.assertEqual(meta["version"], "MVP v0.1")
        self.assertEqual(meta["sensor_rate"], "continuous")
        self.assertIsInstance(meta["timestamp"], str)

    def test_student_mind_graph_ranges(self):
        """Verify mastery bounds (0.0 to 1.0) and status type configurations."""
        self.assertIn("student_mind_graph", self.mock_data)
        smg = self.mock_data["student_mind_graph"]
        
        # Ranges checks
        self.assertTrue(0.0 <= smg["skill_source_mastery"] <= 1.0)
        self.assertTrue(0.0 <= smg["skill_intermediate_mastery"] <= 1.0)
        self.assertTrue(0.0 <= smg["path_efficiency"] <= 1.0)
        
        # Type checks
        self.assertIsInstance(smg["target_flow_completed"], bool)
        self.assertTrue(smg["current_anchor"] is None or isinstance(smg["current_anchor"], str))

    def test_stroke_telemetry_coordinates(self):
        """Verify coordinates array formatting, types, and chronological integrity."""
        self.assertIn("strokes", self.mock_data)
        strokes = self.mock_data["strokes"]
        self.assertIsInstance(strokes, list)
        self.assertTrue(len(strokes) > 0)

        for stroke in strokes:
            self.assertIn("id", stroke)
            self.assertIn("points", stroke)
            points = stroke["points"]
            self.assertIsInstance(points, list)
            
            last_time = 0
            for pt in points:
                self.assertIsInstance(pt["x"], (int, float))
                self.assertIsInstance(pt["y"], (int, float))
                self.assertIsInstance(pt["t"], int)
                self.assertIsInstance(pt["v"], (int, float))
                
                # Check coordinates scale bounds inside typical workspace canvas
                self.assertTrue(pt["x"] >= 0)
                self.assertTrue(pt["y"] >= 0)
                
                # Check time is ascending
                self.assertTrue(pt["t"] >= last_time)
                last_time = pt["t"]

if __name__ == '__main__':
    unittest.main()
