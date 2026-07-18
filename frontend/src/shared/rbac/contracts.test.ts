import { ApiContractError } from "@/shared/api/contracts";
import {
  isRbacPermissionScope,
  parseAdminUser,
  parseAdminUserList,
  parseAssignedRoleList,
  parseAssignedUserList,
  parseRbacPermissionList,
  parseRbacRole,
  parseRbacRolePermission,
  parseUserRoleAssignment,
} from "@/shared/rbac/contracts";

describe("rbac contracts", () => {
  it("recognizes supported and unsupported permission scopes", () => {
    expect(isRbacPermissionScope("own")).toBe(true);
    expect(isRbacPermissionScope("tenant")).toBe(true);
    expect(isRbacPermissionScope("any")).toBe(true);
    expect(isRbacPermissionScope("team")).toBe(false);
  });
  it("parses admin user payload", () => {
    expect(
      parseAdminUser({
        id: 3,
        email: "ops_user",
        disabled: false,
        role_ids: [1, 2],
      }),
    ).toEqual({
      id: 3,
      email: "ops_user",
      disabled: false,
      role_ids: [1, 2],
    });
  });

  it("rejects invalid role_ids payload for admin user", () => {
    expect(() =>
      parseAdminUser({
        id: 3,
        email: "ops_user",
        disabled: false,
        role_ids: ["1"],
      }),
    ).toThrowError(
      new ApiContractError("AdminUser: field 'role_ids[0]' must be number, received string"),
    );
  });

  it("parses role payload with permissions and parent role ids", () => {
    expect(
      parseRbacRole({
        id: 1,
        name: "admin_role",
        permissions: [
          {
            id: "users:manage",
            name: "Manage users",
            scope: "any",
          },
        ],
        parent_role_ids: [2],
      }),
    ).toEqual({
      id: 1,
      name: "admin_role",
      permissions: [
        {
          id: "users:manage",
          name: "Manage users",
          scope: "any",
        },
      ],
      parent_role_ids: [2],
    });
  });

  it("parses role permission assignment payload", () => {
    expect(
      parseRbacRolePermission({
        id: "role_permissions:manage",
        name: "Manage role permissions",
        scope: "tenant",
      }),
    ).toEqual({
      id: "role_permissions:manage",
      name: "Manage role permissions",
      scope: "tenant",
    });
  });

  it("rejects unsupported permission scopes", () => {
    expect(() =>
      parseRbacRolePermission({
        id: "role_permissions:manage",
        name: "Manage role permissions",
        scope: "team",
      }),
    ).toThrowError(
      new ApiContractError(
        "RbacRolePermission: field 'scope' must be one of own, tenant, any, received 'team'",
      ),
    );
  });

  it("parses role and user lists", () => {
    expect(
      parseAdminUserList([
        {
          id: 1,
          email: "admin",
          disabled: false,
          role_ids: [1],
        },
      ]),
    ).toHaveLength(1);

    expect(
      parseRbacPermissionList([
        {
          id: "users:manage",
          name: "Manage users",
        },
      ]),
    ).toHaveLength(1);
  });

  it("parses direct assignment payloads", () => {
    expect(
      parseAssignedRoleList([
        {
          id: 2,
          name: "reader_role",
        },
      ]),
    ).toEqual([
      {
        id: 2,
        name: "reader_role",
      },
    ]);

    expect(
      parseAssignedUserList([
        {
          id: 3,
          email: "reader_user",
          disabled: false,
        },
      ]),
    ).toEqual([
      {
        id: 3,
        email: "reader_user",
        disabled: false,
      },
    ]);

    expect(
      parseUserRoleAssignment({
        user_id: 3,
        role_id: 2,
      }),
    ).toEqual({
      user_id: 3,
      role_id: 2,
    });
  });
});
