import unittest
from compare import build_registry, retrieval_search, measure
class ToolRetrievalContractTests(unittest.TestCase):
    def test_requested_allowed_schema_is_retrievable(self):
        result = retrieval_search(build_registry(), ["read_docs", "search_docs"], "docs")
        self.assertEqual({x["name"] for x in result}, {"read_docs", "search_docs"})
    def test_denied_tool_not_returned_by_client_search(self):
        self.assertEqual(retrieval_search(build_registry(), ["read_docs"], "delete"), [])
        self.assertEqual(retrieval_search(build_registry(), ["read_docs"], "refund"), [])
    def test_server_deferred_is_not_authorization(self):
        v = measure()
        self.assertTrue(v["security_contract"]["server_deferred_headers_contain_unpermitted_names"])
        self.assertTrue(v["security_contract"]["client_discovery_denied_name_not_returned"])
        self.assertEqual(v["api_calls"], 0)
    def test_payload_sizes_are_bytes_only(self):
        v = measure()
        m = v["sizes_bytes_not_model_tokens"]
        self.assertGreater(m["static_full_schema_payload"], m["server_deferred_initial_payload"])
        self.assertIsNone(v["model_token_usage"])
if __name__ == "__main__":
    unittest.main()

