import 'package:flutter_test/flutter_test.dart';
import 'package:ltx_video_app/domain/models.dart';

void main() {
  group('GenerationJob Model', () {
    test('JobStatus should be correctly parsed from JSON', () {
      final json = {
        'job_id': '123-abc',
        'status': 'processing',
        'output_url': null,
        'error': null,
      };

      final job = GenerationJob.fromJson(json);

      expect(job.jobId, '123-abc');
      expect(job.status, JobStatus.processing);
      expect(job.outputUrl, isNull);
    });

    test('Completed JobStatus with output_url should parse correctly', () {
      final json = {
        'job_id': '456-def',
        'status': 'completed',
        'output_url': '/outputs/456-def/video.mp4',
        'error': null,
      };

      final job = GenerationJob.fromJson(json);

      expect(job.jobId, '456-def');
      expect(job.status, JobStatus.completed);
      expect(job.outputUrl, '/outputs/456-def/video.mp4');
    });

    test('Failed JobStatus with error message should parse correctly', () {
      final json = {
        'job_id': '789-ghi',
        'status': 'failed',
        'output_url': null,
        'error': 'Out of memory',
      };

      final job = GenerationJob.fromJson(json);

      expect(job.jobId, '789-ghi');
      expect(job.status, JobStatus.failed);
      expect(job.error, 'Out of memory');
    });
  });
}
