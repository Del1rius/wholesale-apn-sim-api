# Testing Data Limit Validation

## Quick Test Guide

### Frontend Validation Test (Browser)

1. **Access the SIM Detail Page**:
   - Navigate to Dashboard
   - Click on any SIM card to view details
   - Click "Edit Limit" button

2. **Test Invalid Values**:

   **Test Case 1: Value Too High**
   - Enter: `100001`
   - Expected: Red error message "Data limit cannot exceed 100,000 MB"
   - Expected: Submit button disabled
   
   **Test Case 2: Zero or Negative**
   - Enter: `0` or `-100`
   - Expected: Red error message "Data limit must be at least 1 MB"
   - Expected: Submit button disabled
   
   **Test Case 3: Non-numeric**
   - Enter: `abc`
   - Expected: HTML5 validation prevents input or shows error
   
   **Test Case 4: Maximum Valid Value**
   - Enter: `100000`
   - Expected: No error, submit button enabled
   - Expected: Form submits successfully

3. **Verify Real-time Validation**:
   - Type slowly and watch error messages appear immediately
   - Clear invalid value and enter valid value
   - Error should disappear and button should enable

### Backend Validation Test (API)

Use the REST API to test backend validation:

```bash
# Test 1: Create SIM with invalid data limit (too high)
curl -X POST http://localhost:8000/api/inventory/sims/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "iccid": "12345678901234567890",
    "phone_number": "+27123456789",
    "carrier": "Test Carrier",
    "network_type": "4G",
    "data_limit_mb": 150000
  }'

# Expected Response: 400 Bad Request
# Expected Message: "Data limit cannot exceed 100,000 MB."

# Test 2: Create SIM with valid data limit
curl -X POST http://localhost:8000/api/inventory/sims/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "iccid": "12345678901234567890",
    "phone_number": "+27123456789",
    "carrier": "Test Carrier",
    "network_type": "4G",
    "data_limit_mb": 50000
  }'

# Expected Response: 201 Created
# Expected: SIM created successfully

# Test 3: Update existing SIM with invalid limit
curl -X PATCH http://localhost:8000/api/inventory/sims/{sim_id}/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "data_limit_mb": 200000
  }'

# Expected Response: 400 Bad Request
# Expected Message: "Data limit cannot exceed 100,000 MB."
```

### Backend Validation Test (Django Admin)

1. **Access Django Admin**:
   - Navigate to http://localhost:8000/admin/
   - Login with admin credentials
   - Go to Inventory → SIM Cards

2. **Test Creating/Editing**:
   - Try to save a SIM with data_limit_mb > 100,000
   - Expected: Validation error displayed
   - Try to save with valid value (≤ 100,000)
   - Expected: Saves successfully

### View Layer Test (Dashboard Form)

1. **Bypass HTML5 Validation** (using Browser DevTools):
   - Open SIM detail page
   - Click "Edit Limit"
   - Open browser DevTools (F12)
   - Find the input element: `<input id="data_limit_mb" ... max="100000">`
   - Remove the `max` attribute using DevTools
   - Enter a value > 100,000
   - Submit the form

2. **Expected Result**:
   - Form submits to backend
   - Backend view validation catches it
   - Django error message displayed: "Data limit cannot exceed 100,000 MB"
   - User redirected back to form

### Edge Cases to Test

| Test Case | Input Value | Expected Result |
|-----------|-------------|-----------------|
| Minimum valid | `1` | ✓ Accepted |
| Just below minimum | `0` | ✗ Error: "must be at least 1 MB" |
| Negative value | `-100` | ✗ Error: "must be at least 1 MB" |
| Normal value | `5000` | ✓ Accepted |
| Maximum valid | `100000` | ✓ Accepted |
| Just above maximum | `100001` | ✗ Error: "cannot exceed 100,000 MB" |
| Very large value | `999999` | ✗ Error: "cannot exceed 100,000 MB" |
| Empty/null | `` (blank) | ✓ Accepted (field is optional) |
| Decimal value | `100.5` | Converted to `100` (integer) |

### Automation Test Script

For automated testing, you can use this Python test:

```python
from django.test import TestCase
from rest_framework.test import APIClient
from inventory.models import SIMCard
from users.models import Organization, User

class DataLimitValidationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.org = Organization.objects.create(name="Test Org")
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass",
            organization=self.org
        )
        self.client.force_authenticate(user=self.user)
    
    def test_data_limit_too_high(self):
        """Test that data limit above 100,000 MB is rejected"""
        response = self.client.post('/api/inventory/sims/', {
            'iccid': '12345678901234567890',
            'carrier': 'Test Carrier',
            'network_type': '4G',
            'data_limit_mb': 150000
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('100,000', str(response.data))
    
    def test_data_limit_at_maximum(self):
        """Test that data limit of exactly 100,000 MB is accepted"""
        response = self.client.post('/api/inventory/sims/', {
            'iccid': '12345678901234567890',
            'carrier': 'Test Carrier',
            'network_type': '4G',
            'data_limit_mb': 100000,
            'organization': self.org.org_id
        })
        self.assertEqual(response.status_code, 201)
    
    def test_data_limit_too_low(self):
        """Test that data limit of 0 or negative is rejected"""
        response = self.client.post('/api/inventory/sims/', {
            'iccid': '12345678901234567890',
            'carrier': 'Test Carrier',
            'network_type': '4G',
            'data_limit_mb': 0
        })
        self.assertEqual(response.status_code, 400)
```

## Expected Error Messages by Layer

| Validation Layer | Error Message |
|------------------|---------------|
| HTML5 Browser | "Value must be less than or equal to 100000" (browser default) |
| JavaScript | "Data limit cannot exceed 100,000 MB" (red text below input) |
| Django View | "Data limit cannot exceed 100,000 MB" (Django message) |
| DRF Serializer | `{"data_limit_mb": ["Data limit cannot exceed 100,000 MB."]}` |
| Django Model | "Ensure this value is less than or equal to 100000." |

## Visual Indicators

### Valid Input:
- Input field: Normal border
- Submit button: Enabled (blue/primary color)
- No error messages visible

### Invalid Input:
- Input field: May have red border (depending on CSS)
- Error message: Red text below input with icon
- Submit button: Disabled (grayed out)

## Troubleshooting

If validation doesn't work:

1. **Clear browser cache** and reload the page
2. **Check JavaScript console** for errors (F12 → Console tab)
3. **Verify static files** are loaded: check Network tab for `sim_detail.js`
4. **Test API directly** to isolate frontend vs backend issues
5. **Check Django logs** for backend validation errors
