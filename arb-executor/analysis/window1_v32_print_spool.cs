using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Security.Cryptography;
using System.Text;

public static class Window1V32PrintSpool {
    private sealed class Bounds { public double Left; public double Right; }

    private static string StringField(string line, string name) {
        string needle = "\"" + name + "\":\"";
        int start = line.IndexOf(needle, StringComparison.Ordinal);
        if (start < 0) return null;
        start += needle.Length;
        int end = line.IndexOf('"', start);
        return end < 0 ? null : line.Substring(start, end - start);
    }

    private static string NumberField(string line, string name) {
        string needle = "\"" + name + "\":";
        int start = line.IndexOf(needle, StringComparison.Ordinal);
        if (start < 0) return null;
        start += needle.Length;
        int end = start;
        while (end < line.Length && "-+.0123456789eE".IndexOf(line[end]) >= 0) end++;
        return line.Substring(start, end - start);
    }

    private static string JsonString(string value) {
        if (value == null) return "null";
        return "\"" + value.Replace("\\", "\\\\").Replace("\"", "\\\"") + "\"";
    }

    private static string Sha256(string file) {
        using (var stream = File.OpenRead(file))
        using (var hash = SHA256.Create()) {
            byte[] digest = hash.ComputeHash(stream);
            var text = new StringBuilder(digest.Length * 2);
            foreach (byte value in digest) text.Append(value.ToString("x2"));
            return text.ToString();
        }
    }

    public static void Run(string prints, string sourceCsv, string spool, string receiptPath) {
        var sources = new Dictionary<string, Bounds>(StringComparer.Ordinal);
        foreach (string line in File.ReadLines(sourceCsv)) {
            if (String.IsNullOrWhiteSpace(line) || line.StartsWith("ticker,")) continue;
            string[] values = line.Split(',');
            sources.Add(values[0], new Bounds { Left = Double.Parse(values[1], CultureInfo.InvariantCulture), Right = Double.Parse(values[2], CultureInfo.InvariantCulture) });
        }
        Directory.CreateDirectory(spool);
        var closed = new HashSet<string>(StringComparer.Ordinal);
        var seen = new HashSet<string>(StringComparer.Ordinal);
        string current = null;
        bool selected = false;
        StreamWriter writer = null;
        long rawRows = 0, admitted = 0, duplicates = 0;
        Action finish = () => {
            if (writer != null) { writer.Dispose(); writer = null; closed.Add(current); }
            seen = new HashSet<string>(StringComparer.Ordinal);
        };
        using (var input = new StreamReader(new FileStream(prints, FileMode.Open, FileAccess.Read, FileShare.Read, 1 << 20, FileOptions.SequentialScan), Encoding.UTF8, true, 1 << 20)) {
            string line;
            while ((line = input.ReadLine()) != null) {
                if (line.Length == 0) continue;
                rawRows++;
                string ticker = StringField(line, "ticker");
                if (!String.Equals(ticker, current, StringComparison.Ordinal)) {
                    finish(); current = ticker; selected = ticker != null && sources.ContainsKey(ticker);
                    if (selected) {
                        if (closed.Contains(ticker)) throw new InvalidOperationException("non-contiguous print ticker " + ticker);
                        writer = new StreamWriter(Path.Combine(spool, ticker + ".jsonl"), false, new UTF8Encoding(false), 1 << 20);
                    }
                }
                if (!selected || line.IndexOf("\"true_print\":true", StringComparison.Ordinal) < 0) continue;
                string timestamp = StringField(line, "exchange_ts");
                DateTimeOffset parsed;
                if (!DateTimeOffset.TryParse(timestamp, CultureInfo.InvariantCulture, DateTimeStyles.AssumeUniversal, out parsed)) continue;
                double epoch = (parsed.UtcDateTime - new DateTime(1970, 1, 1, 0, 0, 0, DateTimeKind.Utc)).TotalSeconds;
                Bounds bounds = sources[ticker];
                if (epoch < bounds.Left || epoch > bounds.Right) continue;
                string tradeId = StringField(line, "trade_id");
                if (tradeId == null) continue;
                if (!seen.Add(tradeId)) { duplicates++; continue; }
                admitted++;
                string receipt = StringField(line, "receipt_id");
                string price = NumberField(line, "price_cents");
                string size = NumberField(line, "size");
                string taker = StringField(line, "taker_side");
                writer.WriteLine("[" + epoch.ToString("R", CultureInfo.InvariantCulture) + "," + admitted.ToString(CultureInfo.InvariantCulture) + "," + JsonString(receipt) + "," + price + "," + size + "," + JsonString(taker) + "," + JsonString(tradeId) + "]");
            }
        }
        finish();
        string json = "{\n" +
            "  \"path_class\": \"PRIVATE_FIT_DEVELOPMENT_PRINTS_HASH_ONLY\",\n" +
            "  \"sha256\": \"" + Sha256(prints) + "\",\n" +
            "  \"bytes\": " + new FileInfo(prints).Length.ToString(CultureInfo.InvariantCulture) + ",\n" +
            "  \"raw_rows\": " + rawRows.ToString(CultureInfo.InvariantCulture) + ",\n" +
            "  \"admitted_unique_window1_prints\": " + admitted.ToString(CultureInfo.InvariantCulture) + ",\n" +
            "  \"duplicate_trade_id_rows_rejected\": " + duplicates.ToString(CultureInfo.InvariantCulture) + ",\n" +
            "  \"contiguous_ticker_spool_count\": " + closed.Count.ToString(CultureInfo.InvariantCulture) + "\n}\n";
        File.WriteAllText(receiptPath, json, new UTF8Encoding(false));
    }
}
