# GSC-19165-1, "The On-Board Artificial Intelligence Research (OnAIR) Platform"
#
# Copyright © 2023 United States Government as represented by the Administrator of
# the National Aeronautics and Space Administration. No copyright is claimed in the
# United States under Title 17, U.S. Code. All Other Rights Reserved.
#
# Licensed under the NASA Open Source Agreement version 1.3
# See "NOSA GSC-19165-1 OnAIR.pdf"
#
# NOTE: For testing singleton-like classes, a teardown procedure must be implemented
# to delete the instance after every test. Otherwise, proceeding tests will have
# access to the last test's instance. This happens due to the nature of singletons,
# which have a single instance per global scope (which the tests are running in).
#
import pytest
from unittest.mock import MagicMock
from onair.services.service_manager import ServiceManager


def test_ServiceManager__init__raises_ValueError_when_service_dict_is_None_on_first_instantiation(
    mocker,
):
    # Arrange / Act
    with pytest.raises(ValueError) as e_info:
        ServiceManager()

    # Assert
    assert (
        str(e_info.value) == "'service_dict' parameter required on first instantiation"
    )


def test_ServiceManager__init__imports_services_and_sets_attributes(mocker):
    # Arrange
    fake_service_dict = {
        "service1": {"path": "path/to/service1"},
        "service2": {"path": "path/to/service2"},
    }
    fake_imported_services = {"service1": MagicMock(), "service2": MagicMock()}
    mocker.patch(
        "onair.services.service_manager.import_services",
        return_value=fake_imported_services,
    )

    # Act
    service_manager = ServiceManager(fake_service_dict)

    # Assert
    assert service_manager.service1 == fake_imported_services["service1"]
    assert service_manager.service2 == fake_imported_services["service2"]
    assert hasattr(service_manager, "services")

    # Teardown
    del ServiceManager.instance


def test_ServiceManager__init__does_not_reinitialize_if_already_initialized(mocker):
    # Arrange
    fake_service_dict = {"service1": {"path": "path/to/service1"}}
    fake_service_functions = {"service1": {"func1"}}
    mocker.patch.object(ServiceManager, "services", fake_service_functions, create=True)
    mock_import_services = mocker.patch(
        "onair.src.util.service_import.import_services"
    )  # called in __init__

    # Act
    ServiceManager(fake_service_dict)

    # Assert
    assert mock_import_services.call_count == 0

    # Teardown
    del ServiceManager.instance


def test_ServiceManager_get_services_returns_dict_of_services_and_their_functions(
    mocker,
):
    # Arrange
    class FakeService1:
        def func1(self):
            pass

        def _private_func(self):
            pass

    class FakeService2:
        def func2(self):
            pass

        def func3(self):
            pass

    fake_service_dict = {
        "service1": {"path": "path/to/service1"},
        "service2": {"path": "path/to/service2"},
    }

    fake_imported_services = {
        "service1": FakeService1(),
        "service2": FakeService2(),
    }

    mocker.patch(
        "onair.services.service_manager.import_services",
        return_value=fake_imported_services,
    )
    service_manager = ServiceManager(fake_service_dict)

    # Act
    result = service_manager.get_services()

    # Assert
    assert result == {
        "service1": {"func1"},  # correctly avoids _private_func
        "service2": {"func2", "func3"},
    }

    # Teardown
    del ServiceManager.instance


def test_ServiceManager_get_services_returns_empty_dict_when_no_services(mocker):
    # Arrange
    fake_service_dict = {}
    service_manager = ServiceManager(fake_service_dict)

    # Act
    result = service_manager.get_services()

    # Assert
    assert result == {}

    # Teardown
    del ServiceManager.instance


def test_ServiceManager_behaves_as_singleton(mocker):
    # Arrange
    fake_service_dict1 = {"service1": "path1"}
    fake_imported_service = {"service1": MagicMock()}
    mocker.patch(
        "onair.services.service_manager.import_services",
        return_value=fake_imported_service,
    )

    # Act
    service_manager1 = ServiceManager(fake_service_dict1)
    service_manager2 = ServiceManager()

    # Assert
    assert service_manager1 is service_manager2
    assert hasattr(service_manager2, "service1")

    # Teardown
    del ServiceManager.instance
